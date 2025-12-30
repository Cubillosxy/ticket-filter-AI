from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class AuditAttempt:
    ticket_id: str
    request_id: str
    created_at: str
    received_at: str

    subject: str
    description: str
    normalized_hash: str

    category: str
    confidence: float
    decision_path: str
    rules_hit: str | None

    ai_provider: str | None
    ai_model: str | None
    simulate_ai_failure: bool
    fallback_reason: str | None

    latency_total_ms: int
    latency_ai_ms: int | None

    error_type: str | None
    error_message: str | None

    metadata_json: str  # store extra json for flexibility


class AuditStore(Protocol):
    def save_attempt(self, attempt: AuditAttempt) -> None: ...
