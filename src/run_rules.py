
from src.tools.resource_graph import (
    find_unattached_disks,
    find_unattached_public_ips
)

from src.rules.orphan_disk import check_unattached_disks
from src.rules.unused_ip import check_unused_public_ips

from src.pricing.cache import (
    prices_for_disks,
    prices_for_public_ips
)


# 1. Find unattached Azure resources
disks = find_unattached_disks()
unused_ips = find_unattached_public_ips()


# 2. Calculate disk costs
disk_findings = check_unattached_disks(
    disks,
    prices_for_disks(disks)
)


# 3. Calculate Public IP costs
ip_findings = check_unused_public_ips(
    unused_ips,
    prices_for_public_ips(unused_ips)
)


# 4. Combine findings
findings = disk_findings + ip_findings


# 5. Display results
for f in findings:
    print(
        f"[{f.risk.upper()}] {f.resource_name}: "
        f"{f.issue} "
        f"(~${f.est_monthly_cost_usd:.2f}/month) "
        f"-> {f.recommended_action}"
    )


# 6. Display potential savings
total_savings = sum(
    f.est_monthly_cost_usd for f in findings
)

print(f"\nPotential savings: ~${total_savings:.2f}/month")
