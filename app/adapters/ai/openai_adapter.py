from __future__ import annotations

import httpx

from app.adapters.ai.base import AIClassifier, AIResult


class OpenAIClassifier(AIClassifier):
    def __init__(self, api_key: str, model: str, timeout_ms: int) -> None:
        self._api_key = api_key
        self._model = model
        self._timeout = timeout_ms / 1000.0

    async def classify(self, text: str) -> AIResult:

        url = "https://api.openai.com/v1/chat/completions"
        
        # System and user messages for chat completions
        system_message = "You are a ticket classifier. Choose exactly one category from: Billing, Technical Issue, Account / Access, or Other. Return ONLY JSON with keys: category, confidence (0..1)."
        
        user_message = f"Classify this support ticket:\n\n{text}"

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json"
        }

        request_body = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.3,
            "max_tokens": 100
        }

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(
                url,
                headers=headers,
                json=request_body,
            )
            resp.raise_for_status()
            data = resp.json()

        extracted = _extract_json_best_effort(data)
        category = extracted.get("category", "Other")
        confidence = float(extracted.get("confidence", 0.5))
        return AIResult(category=category, confidence=max(0.0, min(1.0, confidence)), raw=data)


def _extract_json_best_effort(data: dict) -> dict:
    """
    Extract JSON from OpenAI Chat Completions response.
    The response format is: data['choices'][0]['message']['content']
    """
    try:
        import json
        
        # First try direct extraction from Chat Completions format
        if 'choices' in data and len(data['choices']) > 0:
            content = data['choices'][0].get('message', {}).get('content', '')
            if content:
                try:
                    return json.loads(content.strip())
                except json.JSONDecodeError:
                    pass  # Fall through to walk method
        
        # Fallback: walk the entire response tree looking for JSON strings
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
                try:
                    return json.loads(s)
                except json.JSONDecodeError:
                    continue
    except Exception:
        return {}
    return {}
