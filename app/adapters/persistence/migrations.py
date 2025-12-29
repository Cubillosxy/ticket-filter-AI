from __future__ import annotations

import sqlite3


def run_sqlite_migrations(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT NOT NULL,
            request_id TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL,
            received_at TEXT NOT NULL,

            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            normalized_hash TEXT NOT NULL,

            category TEXT NOT NULL,
            confidence REAL NOT NULL,
            decision_path TEXT NOT NULL,
            rules_hit TEXT,

            ai_provider TEXT,
            ai_model TEXT,
            simulate_ai_failure INTEGER NOT NULL,
            fallback_reason TEXT,

            latency_total_ms INTEGER NOT NULL,
            latency_ai_ms INTEGER,

            error_type TEXT,
            error_message TEXT,

            metadata_json TEXT NOT NULL
        );
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_ticket_id ON audit_attempts(ticket_id);")
    conn.commit()
