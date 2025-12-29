from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class RuleMatch:
    matched: bool
    category: str
    confidence: float
    rule_name: str | None
    signals: list[str]


_BILLING = [r"\binvoice\b", r"\bbilling\b", r"\bcharge\b", r"\bpayment\b", r"\brefund\b", r"\bsubscription\b"]
_ACCOUNT = [r"\blogin\b", r"\bpassword\b", r"\b2fa\b", r"\baccount\b", r"\baccess\b", r"\blocked\b"]
_TECH = [r"\berror\b", r"\bbug\b", r"\bcrash\b", r"\btimeout\b", r"\b500\b", r"\bstack\b", r"\bapi\b"]


def try_match_rules(text: str) -> RuleMatch:
    t = text.lower()

    def hit(patterns: list[str]) -> list[str]:
        found = []
        for p in patterns:
            if re.search(p, t):
                found.append(p.strip(r"\b"))
        return found

    billing = hit(_BILLING)
    if billing:
        return RuleMatch(True, "Billing", 0.95, "billing_keywords", billing)

    account = hit(_ACCOUNT)
    if account:
        return RuleMatch(True, "Account / Access", 0.93, "account_keywords", account)

    tech = hit(_TECH)
    if tech:
        return RuleMatch(True, "Technical Issue", 0.90, "technical_keywords", tech)

    return RuleMatch(False, "Other", 0.0, None, [])
