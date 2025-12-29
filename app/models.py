from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class Category(str, Enum):
    BILLING = "Billing"
    TECHNICAL = "Technical Issue"
    ACCOUNT = "Account / Access"
    OTHER = "Other"


@dataclass(frozen=True)
class Ticket:
    id: str
    subject: str
    description: str
    created_at: str  # string for now, change to datetime later


@dataclass(frozen=True)
class Classification:
    category: Category
    confidence: float
    metadata: dict[str, Any]
