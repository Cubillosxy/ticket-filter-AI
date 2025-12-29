from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FallbackResult:
    category: str
    confidence: float
    signals: list[str]


# Lightweight scoring baseline (acts like a "tiny local model")
_SCORES = {
    "Billing": ["invoice", "billing", "charge", "payment", "refund", "subscription"],
    "Account / Access": ["login", "password", "2fa", "account", "access", "locked"],
    "Technical Issue": ["error", "bug", "crash", "timeout", "stack", "api", "500"],
}


def classify_with_scoring(text: str) -> FallbackResult:
    t = text.lower()
    best_cat = "Other"
    best_score = 0
    best_signals: list[str] = []

    for cat, keywords in _SCORES.items():
        score = 0
        signals: list[str] = []
        for kw in keywords:
            if kw in t:
                score += 1
                signals.append(kw)
        if score > best_score:
            best_score = score
            best_cat = cat
            best_signals = signals

    if best_score == 0:
        return FallbackResult("Other", 0.35, [])

    # Simple mapping score -> confidence
    confidence = min(0.80, 0.45 + 0.10 * best_score)
    return FallbackResult(best_cat, confidence, best_signals)
