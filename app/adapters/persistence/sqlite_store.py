from __future__ import annotations

import sqlite3
from pathlib import Path

from app.adapters.persistence.base import AuditAttempt, AuditStore
from app.adapters.persistence.migrations import run_sqlite_migrations


class SQLiteAuditStore(AuditStore):
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self._db_path)
        try:
            run_sqlite_migrations(conn)
        finally:
            conn.close()

    def save_attempt(self, attempt: AuditAttempt) -> None:
        conn = sqlite3.connect(self._db_path)
        try:
            conn.execute(
                """
                INSERT INTO audit_attempts (
                    ticket_id, request_id, created_at, received_at,
                    subject, description, normalized_hash,
                    category, confidence, decision_path, rules_hit,
                    ai_provider, ai_model, simulate_ai_failure, fallback_reason,
                    latency_total_ms, latency_ai_ms,
                    error_type, error_message,
                    metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    attempt.ticket_id,
                    attempt.request_id,
                    attempt.created_at,
                    attempt.received_at,
                    attempt.subject,
                    attempt.description,
                    attempt.normalized_hash,
                    attempt.category,
                    attempt.confidence,
                    attempt.decision_path,
                    attempt.rules_hit,
                    attempt.ai_provider,
                    attempt.ai_model,
                    1 if attempt.simulate_ai_failure else 0,
                    attempt.fallback_reason,
                    attempt.latency_total_ms,
                    attempt.latency_ai_ms,
                    attempt.error_type,
                    attempt.error_message,
                    attempt.metadata_json,
                ),
            )
            conn.commit()
        finally:
            conn.close()
