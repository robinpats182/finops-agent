
from .models import Finding, risk_from_tags

HOURS_PER_MONTH = 730
DEFAULT_IP_MONTHLY_COST = 100

def check_unused_public_ips(
    ips: list[dict],
    prices_by_region: dict[str, dict[str, float]] | None = None
) -> list[Finding]:

    prices_by_region = prices_by_region or {}
    findings = []

    for ip in ips:
        region = (ip.get("location") or "").lower()
        sku = ip.get("sku", "Unknown")
        version = ip.get("ipVersion", "Any")
        allocation = ip.get("allocation", "Unknown")

        region_prices = prices_by_region.get(region, {})

        hourly_price = region_prices.get(
            f"{sku}|{version}",
            region_prices.get(f"{sku}|Any")
        )

        if hourly_price is not None:
            estimated_cost = round(
                hourly_price * HOURS_PER_MONTH, 2
            )
            pricing_issue = ""
        elif not prices_by_region and sku == "Standard" and allocation == "Static":
            estimated_cost = 3.65
            pricing_issue = ""
        else:
            estimated_cost = 0.0
            pricing_issue = " - pricing unavailable"
        
        issue = ( f"Public IP ({sku}, {version}, " 
                 f"{allocation}) is not attached"
                 + pricing_issue )
        
        findings.append(
            Finding(
                rule="unused_public_ip",
                resource_name=ip["name"],
                resource_group=ip["resourceGroup"],
                issue=issue,
                est_monthly_cost_usd=estimated_cost,
                risk=risk_from_tags(ip.get("tags")),
                recommended_action="Delete the public IP",
                resource_id=ip.get("id", "")
            )
        )

    return findings