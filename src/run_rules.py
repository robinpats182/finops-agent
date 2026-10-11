from src.tools.resource_graph import find_unattached_disks, find_unattached_public_ips
from src.rules.orphan_disk import check_unattached_disks
from src.rules.unused_ip import check_unused_public_ips

findings = check_unattached_disks(find_unattached_disks()) + \
           check_unused_public_ips(find_unattached_public_ips())

for f in findings:
    print(f"[{f.risk.upper()}] {f.resource_name}: {f.issue} "
          f"(~${f.est_monthly_cost_usd}/month) -> {f.recommended_action}")

print(f"\nPotential savings: ~${sum(f.est_monthly_cost_usd for f in findings):.2f}/month")