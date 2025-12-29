from __future__ import annotations

from pydantic import BaseModel, Field


class TicketIn(BaseModel):
    id: str = Field(min_length=1)
    subject: str = Field(default="")
    description: str = Field(default="")
    created_at: str = Field(min_length=1)


class ClassificationOut(BaseModel):
    category: str
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: dict
