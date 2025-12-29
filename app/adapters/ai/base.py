from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class AIResult:
    category: str
    confidence: float
    raw: dict


class AIClassifier(Protocol):
    async def classify(self, text: str) -> AIResult: ...
