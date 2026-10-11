import json
from dataclasses import dataclass, asdict

from src.rules.models import Finding
from .llm import LLM

RISK_ORDER = {"low": 0, "medium": 1, "high": 2}

SYSTEM_PROMPT = (
    "You are a cloud cost assistant. Summarise the findings for the owner in "
    "3-5 plain sentences. Use ONLY the facts provided. Never invent numbers "
    "or resources. Mention any high-risk items explicitly."
)


@dataclass(frozen=True)
class Proposal:
    summary: str
    findings: list[Finding]
    total_monthly_savings_usd: float
    requires_approval: bool


def build_proposal(findings: list[Finding], llm: LLM) -> Proposal:
    # Code decides order and totals; the LLM never touches the numbers.
    ordered = sorted(
        findings,
        key=lambda f: (-f.est_monthly_cost_usd, RISK_ORDER[f.risk]),
    )
    total = round(sum(f.est_monthly_cost_usd for f in ordered), 2)

    facts = json.dumps(
        {"findings": [asdict(f) for f in ordered], "total": total}, indent=2
    )
    summary = llm.complete(SYSTEM_PROMPT, facts) if ordered else "No waste found."

    return Proposal(
        summary=summary,
        findings=ordered,
        total_monthly_savings_usd=total,
        requires_approval=bool(ordered),  # always true when anything is proposed
    )