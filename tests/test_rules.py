from src.rules.orphan_disk import check_unattached_disks
from src.rules.unused_ip import check_unused_public_ips


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