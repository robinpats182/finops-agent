from src.rules.orphan_disk import check_unattached_disks
from src.rules.unused_ip import check_unused_public_ips
from src.rules.orphan_disk import check_unattached_disks


def disk(**overrides):
    base = {"name": "d", "resourceGroup": "rg", "sizeGb": 10,
            "sku": "Standard_LRS", "tags": None}
    base.update(overrides)
    return base


def test_unattached_disk_is_flagged():
    assert len(check_unattached_disks([disk()])) == 1


def test_attached_disk_is_never_flagged():
    attached = disk(managedBy="/subscriptions/x/virtualMachines/vm1")
    assert check_unattached_disks([attached]) == []


def test_disk_in_reserved_state_is_skipped():
    assert check_unattached_disks([disk(diskState="Reserved")]) == []


def test_missing_size_does_not_crash():
    findings = check_unattached_disks([disk(sizeGb=None)])
    assert len(findings) == 1
    assert findings[0].est_monthly_cost_usd == 0.0
    assert "size unknown" in findings[0].issue


def make_disk(**overrides):
    base = {"name": "d1", "resourceGroup": "rg", "sizeGb": 4,
            "sku": "Standard_LRS", "tags": {}}
    return {**base, **overrides}


def make_ip(**overrides):
    base = {"name": "ip1", "resourceGroup": "rg", "sku": "Standard",
            "allocation": "Static", "tags": {}}
    return {**base, **overrides}


def test_unattached_disk_is_flagged_with_cost():
    f = check_unattached_disks([make_disk(sizeGb=100)])[0]
    assert f.rule == "unattached_disk"
    assert f.est_monthly_cost_usd == 5.0


def test_untagged_resource_is_medium_risk():
    assert check_unattached_disks([make_disk()])[0].risk == "medium"


def test_prod_tagged_resource_is_high_risk():
    f = check_unattached_disks([make_disk(tags={"env": "prod"})])[0]
    assert f.risk == "high"


def test_other_tags_are_low_risk():
    f = check_unattached_disks([make_disk(tags={"owner": "me"})])[0]
    assert f.risk == "low"


def test_no_disks_no_findings():
    assert check_unattached_disks([]) == []


def test_static_standard_ip_costs_money():
    assert check_unused_public_ips([make_ip()])[0].est_monthly_cost_usd == 3.65


def test_dynamic_ip_is_free():
    f = check_unused_public_ips([make_ip(allocation="Dynamic")])[0]
    assert f.est_monthly_cost_usd == 0.0
    
PRICES = {"germanywestcentral": {"S4 LRS Disk": 1.536}}


def test_real_tier_price_is_used_when_available():
    f = check_unattached_disks(
        [disk(sizeGb=4, location="germanywestcentral")], PRICES)[0]
    assert f.est_monthly_cost_usd == 1.54
    assert f.cost_basis == "tier_price"
    assert "estimated" not in f.issue


def test_missing_price_falls_back_to_flagged_estimate():
    f = check_unattached_disks(
        [disk(sizeGb=4, location="germanywestcentral")], {})[0]
    assert f.cost_basis == "estimate"
    assert "[price estimated]" in f.issue


def test_unknown_region_falls_back_to_flagged_estimate():
    f = check_unattached_disks([disk(sizeGb=4)], PRICES)[0]
    assert f.cost_basis == "estimate"