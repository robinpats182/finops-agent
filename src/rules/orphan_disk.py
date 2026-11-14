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
        # Re-check in code: never trust that the query already filtered.
        if d.get("managedBy"):
            continue                      # attached to a VM
        if d.get("diskState") not in (None, "Unattached"):
            continue                      # e.g. Reserved, ActiveSAS
        size = d.get("sizeGb")
        if size is None:
            cost = 0.0
            detail = f"Disk (size unknown, {d.get('sku')})"
        else:
            cost = round(size * PRICE_PER_GB_MONTH.get(d.get("sku"), 0.10), 2)
            detail = f"Disk ({size} GB, {d.get('sku')})"
        findings.append(
            Finding(
                rule="unattached_disk",
                resource_name=d["name"],
                resource_group=d["resourceGroup"],
                issue=f"{detail} is not attached to any VM",
                est_monthly_cost_usd=cost,
                risk=risk_from_tags(d.get("tags")),
                recommended_action="Snapshot if needed, then delete the disk",
                resource_id=d.get("id", ""),
            )
        )
    return findings