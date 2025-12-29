from __future__ import annotations

from fastapi import FastAPI

from app.adapters.ai.openai_adapter import OpenAIClassifier
from app.adapters.ai.stub_adapter import StubAIClassifier
from app.adapters.persistence.sqlite_store import SQLiteAuditStore
from app.core.config import settings
from app.core.logging import setup_logging
from app.services.orchestrator import TicketClassifierOrchestrator
from app.api.routes import router


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title=settings.app_name)
    app.include_router(router)
    return app


_app = create_app()


def get_orchestrator() -> TicketClassifierOrchestrator:
    audit = SQLiteAuditStore(settings.audit_db_path)

    ai = None
    ai_provider = settings.ai_provider # default
    ai_model = None

    if settings.ai_provider == "openai":
        if not settings.openai_api_key:
            ai_provider = "none"
        else:
            ai = OpenAIClassifier(
                api_key=settings.openai_api_key,
                model=settings.openai_model,
                timeout_ms=settings.ai_timeout_ms,
            )
            ai_model = settings.openai_model

    if settings.ai_provider == "stub":
        ai = StubAIClassifier()
        ai_provider = "stub"
        ai_model = "stub"

    return TicketClassifierOrchestrator(audit_store=audit, ai=ai, ai_provider=ai_provider, ai_model=ai_model)


app = _app
