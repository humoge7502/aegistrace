"""Default policy rules (ADR-003).

Policies are per-tenant rows; missing fields fall back to these defaults.
Rules are intentionally explicit and explainable — no opaque scores.
"""

from __future__ import annotations

from backend.app.domain.enums import Severity, TrustState

DEFAULT_RULES: dict = {
    # deviation severity -> resulting execution trust state
    "critical": TrustState.UNTRUSTED.value,
    "high": TrustState.UNTRUSTED.value,
    "medium": TrustState.DEGRADED.value,
    "low": TrustState.DEGRADED.value,
    # execution with no registered baseline
    "no_baseline": TrustState.UNKNOWN.value,  # UNKNOWN != TRUSTED (ADR-003)
    # when an execution is judged UNTRUSTED, also quarantine its outputs
    "quarantine_outputs": True,
    # issue an AI Trust Certificate for TRUSTED completed executions
    "certify_trusted": True,
    # compromise propagation scope: all_history (conservative) | from_compromise_time
    "compromised_propagation": "all_history",
}


def effective_rules(policy_rules: dict | None) -> dict:
    rules = dict(DEFAULT_RULES)
    if policy_rules:
        rules.update(policy_rules)
    return rules


def severity_rank(sev: str | Severity) -> int:
    order = [Severity.INFO.value, Severity.LOW.value, Severity.MEDIUM.value,
             Severity.HIGH.value, Severity.CRITICAL.value]
    return order.index(sev if isinstance(sev, str) else sev.value)


def worst_severity(sevs: list[str | Severity]) -> str | None:
    if not sevs:
        return None
    return max(sevs, key=severity_rank)
