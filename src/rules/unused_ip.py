from .models import Finding, risk_from_tags

# Rough USD per month for an unattached static IP. Placeholder values.
STATIC_IP_COST = {"Standard": 3.65, "Basic": 2.63}


def check_unused_public_ips(ips: list[dict]) -> list[Finding]:
    findings = []
    for ip in ips:
        cost = (
            STATIC_IP_COST.get(ip["sku"], 0.0)
            if ip.get("allocation") == "Static"
            else 0.0
        )
        findings.append(
            Finding(
                rule="unused_public_ip",
                resource_name=ip["name"],
                resource_group=ip["resourceGroup"],
                issue=f"Public IP ({ip['sku']}, {ip.get('allocation')}) is not attached",
                est_monthly_cost_usd=cost,
                risk=risk_from_tags(ip.get("tags")),
                recommended_action="Delete the public IP",
            )
        )
    return findings