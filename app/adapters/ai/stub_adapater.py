from __future__ import annotations

from app.adapters.ai.base import AIClassifier, AIResult


class StubAIClassifier(AIClassifier):
    async def classify(self, text: str) -> AIResult:
        # deterministic stub for local/dev
        return AIResult(category="Other", confidence=0.40, raw={"provider": "stub"})
