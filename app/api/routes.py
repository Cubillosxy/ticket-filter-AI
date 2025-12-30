from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.schemas import ClassificationOut, TicketIn
from app.dependencies import get_orchestrator

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/v1/tickets/classify", response_model=ClassificationOut)
async def classify_ticket(
    payload: TicketIn,
    simulate_ai_failure: bool = Query(default=False),
    force_ai: bool = Query(default=False),
    orchestrator=Depends(get_orchestrator),
) -> dict:
    return await orchestrator.classify(
        ticket_id=payload.id,
        subject=payload.subject,
        description=payload.description,
        created_at=payload.created_at,
        simulate_ai_failure=simulate_ai_failure,
        force_ai=force_ai,
    )
