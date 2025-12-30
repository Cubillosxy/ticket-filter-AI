from __future__ import annotations

import httpx

from app.adapters.ai.base import AIClassifier, AIResult


class OpenAIClassifier(AIClassifier):
    def __init__(self, api_key: str, model: str, timeout_ms: int) -> None:
        self._api_key = api_key
        self._model = model
        self._timeout = timeout_ms / 1000.0

    async def classify(self, text: str) -> AIResult:

        url = "https://api.openai.com/v1/responses"
        # minimal prompt
        prompt = (
            "You are a ticket classifier. Choose exactly one category from:\n"
            "- Billing\n- Technical Issue\n- Account / Access\n- Other\n\n"
            "Return ONLY JSON with keys: category, confidence (0..1).\n\n"
            f"Ticket:\n{text}\n"
        )

        headers = {"Authorization": f"Bearer {self._api_key}"}

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(
                url,
                headers=headers,
                json={
                    "model": self._model,
                    "input": prompt,
                },
            )
            resp.raise_for_status()
            data = resp.json()

        extracted = _extract_json_best_effort(data)
        category = extracted.get("category", "Other")
        confidence = float(extracted.get("confidence", 0.5))
        return AIResult(category=category, confidence=max(0.0, min(1.0, confidence)), raw=data)


def _extract_json_best_effort(data: dict) -> dict:

    try:
        import json

        def walk(obj):
            if isinstance(obj, dict):
                for v in obj.values():
                    yield from walk(v)
            elif isinstance(obj, list):
                for i in obj:
                    yield from walk(i)
            elif isinstance(obj, str):
                yield obj

        for s in walk(data):
            s = s.strip()
            if s.startswith("{") and s.endswith("}"):
                return json.loads(s)
    except Exception:
        return {}
    return {}
