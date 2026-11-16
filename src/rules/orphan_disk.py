from .models import Finding, risk_from_tags
from src.pricing.tiers import disk_tier, meter_name

# Rough USD per GB-month. Placeholder: replace later with the
# Azure Retail Prices API (public, no login needed).
PRICE_PER_GB_MONTH = {
    "Standard_LRS": 0.05,
    "StandardSSD_LRS": 0.08,
    "Premium_LRS": 0.15,
}



def check_unattached_disks(disks: list[dict],
                           prices_by_region: dict | None = None) -> list[Finding]:
    prices_by_region = prices_by_region or {}
    findings = []
    for d in disks:
        if d.get("managedBy"):
            continue                      # attached to a VM
        if d.get("diskState") not in (None, "Unattached"):
            continue                      # e.g. Reserved, ActiveSAS
        sku, size = d.get("sku"), d.get("sizeGb")
        basis = "estimate"
        if size is None:
            cost, detail = 0.0, f"Disk (size unknown, {sku})"
        else:
            detail = f"Disk ({size} GB, {sku})"
            cost = None
            tier = disk_tier(sku, size)
            if tier:
                region = (d.get("location") or "").lower()
                price = prices_by_region.get(region, {}).get(meter_name(*tier))
                if price is not None:
                    cost, basis = price, "tier_price"
            if cost is None:               # no exact price: flagged estimate
                cost = size * PRICE_PER_GB_MONTH.get(sku, 0.10)
            cost = round(cost, 2)
        note = "" if basis == "tier_price" else " [price estimated]"
        findings.append(
            Finding(
                rule="unattached_disk",
                resource_name=d["name"],
                resource_group=d["resourceGroup"],
                issue=f"{detail} is not attached to any VM{note}",
                est_monthly_cost_usd=cost,
                risk=risk_from_tags(d.get("tags")),
                recommended_action="Snapshot if needed, then delete the disk",
                resource_id=d.get("id", ""),
                cost_basis=basis,
            )
        )
    return findings
