import pytest
from src.pricing.tiers import disk_tier, meter_name


@pytest.mark.parametrize("sku,size,expected", [
    ("Standard_LRS", 4, ("S4", "LRS")),        # your orphan-disk-01
    ("Standard_LRS", 32, ("S4", "LRS")),       # exactly on a boundary
    ("Standard_LRS", 33, ("S6", "LRS")),       # one over rounds UP
    ("Standard_LRS", 128, ("S10", "LRS")),
    ("Premium_LRS", 5, ("P2", "LRS")),
    ("StandardSSD_LRS", 100, ("E10", "LRS")),
    ("Premium_ZRS", 64, ("P6", "ZRS")),
])
def test_size_rounds_up_to_tier(sku, size, expected):
    assert disk_tier(sku, size) == expected


@pytest.mark.parametrize("sku,size", [
    ("UltraSSD_LRS", 100),        # billed per provisioned unit, not by tier
    ("PremiumV2_LRS", 100),
    ("Standard_LRS", None),       # size unknown
    ("Standard_LRS", 0),
    ("Standard_LRS", 40000),      # bigger than any tier
    (None, 10),
])
def test_unknown_inputs_return_none(sku, size):
    assert disk_tier(sku, size) is None


def test_meter_name():
    assert meter_name("S4", "LRS") == "S4 LRS Disk"