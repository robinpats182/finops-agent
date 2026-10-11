from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    rule: str
    resource_name: str
    resource_group: str
    issue: str
    est_monthly_cost_usd: float
    risk: str  # "low" | "medium" | "high"
    recommended_action: str


def risk_from_tags(tags: dict | None) -> str:
    """Protected env -> high, no tags (owner unknown) -> medium, else low."""
    tags = tags or {}
    if str(tags.get("env", "")).lower() in {"prod", "production"}:
        return "high"
    if not tags:
        return "medium"
    return "low"