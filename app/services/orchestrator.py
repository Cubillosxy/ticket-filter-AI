from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import asdict
from datetime import datetime, timezone

from app.adapters.ai.base import AIClassifier
from app.adapters.persistence.base import AuditAttempt, AuditStore
from app.services.fallback import classify_with_scoring
from app.services.rules import try_match_rules


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_text(subject: str, description: str) -> str:
    s = (subject or "").strip()
    d = (description or "").strip()
    return f"{s}\n\n{d}".strip()


class TicketClassifierOrchestrator:
    def __init__(self, audit_store: AuditStore, ai: AIClassifier | None, ai_provider: str, ai_model: str | None) -> None:
        self._audit = audit_store
        self._ai = ai
        self._ai_provider = ai_provider
        self._ai_model = ai_model

    async def classify(
        self,
        ticket_id: str,
        subject: str,
        description: str,
        created_at: str,
        simulate_ai_failure: bool,
        force_ai: bool = False,
    ) -> dict:
        request_id = str(uuid.uuid4())
        received_at = _utc_now_iso()

        text = normalize_text(subject, description)
        normalized_hash = _hash_text(text)

        start = time.perf_counter()

        # 1) Rules (skip if force_ai is enabled)
        rule = try_match_rules(text)
        if rule.matched and not force_ai:
            total_ms = int((time.perf_counter() - start) * 1000)
            result = {
                "category": rule.category,
                "confidence": rule.confidence,
                "metadata": {
                    "request_id": request_id,
                    "decision_path": ["rules"],
                    "signals": rule.signals,
                    "fallback_used": False,
                    "reprocess_enqueued": False,
                },
            }
            self._save_attempt(
                ticket_id=ticket_id,
                request_id=request_id,
                created_at=created_at,
                received_at=received_at,
                subject=subject,
                description=description,
                normalized_hash=normalized_hash,
                result=result,
                decision_path="rules",
                rules_hit=rule.rule_name,
                simulate_ai_failure=simulate_ai_failure,
                fallback_reason=None,
                latency_total_ms=total_ms,
                latency_ai_ms=None,
                error_type=None,
                error_message=None,
                extra_metadata={"rule": asdict(rule)},
            )
            return result

        # 2) AI (optional)
        ai_latency_ms: int | None = None
        ai_error_type: str | None = None
        ai_error_message: str | None = None
        if self._ai is not None and not simulate_ai_failure:
            ai_start = time.perf_counter()
            try:
                ai_res = await self._ai.classify(text)
                ai_latency_ms = int((time.perf_counter() - ai_start) * 1000)
                total_ms = int((time.perf_counter() - start) * 1000)

                decision_path_list = ["rules:skipped", "ai"] if force_ai else ["rules:no_match", "ai"]
                result = {
                    "category": ai_res.category,
                    "confidence": ai_res.confidence,
                    "metadata": {
                        "request_id": request_id,
                        "decision_path": decision_path_list,
                        "ai_provider": self._ai_provider,
                        "model": self._ai_model,
                        "latency_ms": {"total": total_ms, "ai": ai_latency_ms},
                        "fallback_used": False,
                        "signals": [],
                        "reprocess_enqueued": False,
                    },
                }
                decision_path_str = "force_ai>ai" if force_ai else "rules>ai"
                self._save_attempt(
                    ticket_id=ticket_id,
                    request_id=request_id,
                    created_at=created_at,
                    received_at=received_at,
                    subject=subject,
                    description=description,
                    normalized_hash=normalized_hash,
                    result=result,
                    decision_path=decision_path_str,
                    rules_hit=None,
                    simulate_ai_failure=simulate_ai_failure,
                    fallback_reason=None,
                    latency_total_ms=total_ms,
                    latency_ai_ms=ai_latency_ms,
                    error_type=None,
                    error_message=None,
                    extra_metadata={"ai_raw": ai_res.raw},
                )
                return result
            except Exception as e:
                ai_latency_ms = int((time.perf_counter() - ai_start) * 1000)
                ai_error_type = type(e).__name__
                ai_error_message = str(e)

        if simulate_ai_failure:
            ai_error_type = "SimulatedFailure"
            ai_error_message = "simulate_ai_failure=true"

        # 3) Fallback local
        fb = classify_with_scoring(text)
        total_ms = int((time.perf_counter() - start) * 1000)

        needs_reprocess = ai_error_type is not None and fb.confidence < 0.70

        result = {
            "category": fb.category,
            "confidence": fb.confidence,
            "metadata": {
                "request_id": request_id,
                "decision_path": ["rules:no_match", "fallback_local"],
                "fallback_used": True,
                "fallback_reason": ai_error_type or "ai_disabled",
                "signals": fb.signals,
                "latency_ms": {"total": total_ms, "ai": ai_latency_ms},
                "needs_reprocess": needs_reprocess,
                # future: if async enabled -> enqueue job
                "reprocess_enqueued": False,
            },
        }

        self._save_attempt(
            ticket_id=ticket_id,
            request_id=request_id,
            created_at=created_at,
            received_at=received_at,
            subject=subject,
            description=description,
            normalized_hash=normalized_hash,
            result=result,
            decision_path="rules>fallback_local",
            rules_hit=None,
            simulate_ai_failure=simulate_ai_failure,
            fallback_reason=ai_error_type or "ai_disabled",
            latency_total_ms=total_ms,
            latency_ai_ms=ai_latency_ms,
            error_type=ai_error_type,
            error_message=ai_error_message,
            extra_metadata={},
        )
        return result

    def _save_attempt(
        self,
        ticket_id: str,
        request_id: str,
        created_at: str,
        received_at: str,
        subject: str,
        description: str,
        normalized_hash: str,
        result: dict,
        decision_path: str,
        rules_hit: str | None,
        simulate_ai_failure: bool,
        fallback_reason: str | None,
        latency_total_ms: int,
        latency_ai_ms: int | None,
        error_type: str | None,
        error_message: str | None,
        extra_metadata: dict,
    ) -> None:
        attempt = AuditAttempt(
            ticket_id=ticket_id,
            request_id=request_id,
            created_at=created_at,
            received_at=received_at,
            subject=subject or "",
            description=description or "",
            normalized_hash=normalized_hash,
            category=result["category"],
            confidence=float(result["confidence"]),
            decision_path=decision_path,
            rules_hit=rules_hit,
            ai_provider=self._ai_provider if "ai" in decision_path else None,
            ai_model=self._ai_model if "ai" in decision_path else None,
            simulate_ai_failure=simulate_ai_failure,
            fallback_reason=fallback_reason,
            latency_total_ms=latency_total_ms,
            latency_ai_ms=latency_ai_ms,
            error_type=error_type,
            error_message=error_message,
            metadata_json=json.dumps({"result": result.get("metadata", {}), **extra_metadata}, ensure_ascii=False),
        )
        self._audit.save_attempt(attempt)
