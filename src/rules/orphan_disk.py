from .models import Finding, risk_from_tags

# Rough USD per GB-month. Placeholder: replace later with the
# Azure Retail Prices API (public, no login needed).
PRICE_PER_GB_MONTH = {
    "Standard_LRS": 0.05,
    "StandardSSD_LRS": 0.08,
    "Premium_LRS": 0.15,
}


def check_unattached_disks(disks: list[dict]) -> list[Finding]:
    findings = []
    for d in disks:
        price = PRICE_PER_GB_MONTH.get(d["sku"], 0.10)
        findings.append(
            Finding(
                rule="unattached_disk",
                resource_name=d["name"],
                resource_group=d["resourceGroup"],
                issue=f"Disk ({d['sizeGb']} GB, {d['sku']}) is not attached to any VM",
                est_monthly_cost_usd=round(d["sizeGb"] * price, 2),
                risk=risk_from_tags(d.get("tags")),
                recommended_action="Snapshot if needed, then delete the disk",
            )
        )
    return findings