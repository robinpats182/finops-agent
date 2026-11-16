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
    resource_id: str = ""
    cost_basis: str = "estimate"   # "tier_price" = real Azure list price


ENV_KEYS = {"env", "environment", "stage"}
PROTECTED_VALUES = {"prod", "production", "prd", "live"}
PROTECT_KEYS = {"do-not-delete", "donotdelete"}
FALSE_VALUES = {"false", "no", "0"}


def risk_from_tags(tags: dict | None) -> str:
    """Protected -> high, no tags (owner unknown) -> medium, else low.

    Tag names and values are compared case-insensitively and trimmed,
    because people write Env, ENV, Environment, Production, PRD, etc.
    """
    if not tags:
        return "medium"
    norm = {str(k).strip().lower(): str(v).strip().lower()
            for k, v in tags.items()}
    if any(norm.get(k) in PROTECTED_VALUES for k in ENV_KEYS):
        return "high"
    if any(k in norm and norm[k] not in FALSE_VALUES for k in PROTECT_KEYS):
        return "high"
    return "low"