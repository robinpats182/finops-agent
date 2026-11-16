import json
from pathlib import Path
from src.pricing.retail_prices import parse_disk_prices

FIXTURE = Path(__file__).parent / "fixtures" / "disk_prices_sample.json"


def load_items():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))["Items"]


def test_monthly_tier_price_is_kept():
    assert parse_disk_prices(load_items())["E1 ZRS Disk"] == 0.45


def test_operations_meter_is_not_mistaken_for_a_disk_price():
    prices = parse_disk_prices(load_items())
    assert "E60 ZRS Disk Operations" not in prices
    # Every key must be a per-disk meter, never a transactions meter.
    assert prices
    assert all(name.endswith(" Disk") for name in prices)
    # The tiny "per 10K operations" price must not leak in as a disk price.
    assert all(price >= 0.01 for price in prices.values())


def test_conflicting_prices_for_one_meter_are_dropped():
    items = load_items()
    conflicting = dict(items[1], retailPrice=0.99)
    assert "E1 ZRS Disk" not in parse_disk_prices(items + [conflicting])


def test_identical_duplicates_are_fine():
    items = load_items()
    assert parse_disk_prices(items + [items[1]])["E1 ZRS Disk"] == 0.45

def test_real_s4_items_give_the_monthly_price_only():
    path = Path(__file__).parent / "fixtures" / "s4_prices.json"
    items = json.loads(path.read_text(encoding="utf-8"))["Items"]
    assert parse_disk_prices(items) == {"S4 LRS Disk": 1.536}