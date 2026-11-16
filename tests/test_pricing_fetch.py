import json
import pytest
from src.pricing.client import build_url, fetch_disk_items
from src.pricing.cache import load_prices

REGION = "germanywestcentral"
NEXT = "https://prices.azure.com/api/retail/prices?page=2"


def page(items, nxt=None):
    return {"Items": items, "NextPageLink": nxt}


def test_follows_next_page_link():
    pages = {build_url(REGION): page([{"n": 1}], NEXT), NEXT: page([{"n": 2}])}
    items = fetch_disk_items(REGION, get_json=lambda u: pages[u])
    assert [i["n"] for i in items] == [1, 2]


def test_rejects_next_link_on_another_host():
    pages = {build_url(REGION): page([], "https://evil.example.com/x")}
    with pytest.raises(ValueError):
        fetch_disk_items(REGION, get_json=lambda u: pages[u])


def test_page_limit_stops_endless_paging():
    with pytest.raises(RuntimeError):
        fetch_disk_items(REGION, get_json=lambda u: page([], NEXT))


def test_region_is_validated():
    with pytest.raises(ValueError):
        build_url("x' or 1 eq 1")


# --- cache. The prices below are synthetic test values, not real Azure prices.
ITEM = {"type": "Consumption", "unitOfMeasure": "1/Month",
        "productName": "Standard HDD Managed Disks",
        "meterName": "X1 LRS Disk", "retailPrice": 1.0}


def boom(region):
    raise AssertionError("network must not be used")


def test_fetch_then_cache(tmp_path):
    prices = load_prices(REGION, fetch=lambda r: [ITEM], now=lambda: 1000.0,
                         cache_dir=tmp_path)
    assert prices == {"X1 LRS Disk": 1.0}
    assert (tmp_path / f"disk_prices_{REGION}.json").exists()


def test_fresh_cache_skips_network(tmp_path):
    load_prices(REGION, fetch=lambda r: [ITEM], now=lambda: 1000.0,
                cache_dir=tmp_path)
    assert load_prices(REGION, fetch=boom, now=lambda: 2000.0,
                       cache_dir=tmp_path) == {"X1 LRS Disk": 1.0}


def test_stale_cache_is_refreshed(tmp_path):
    load_prices(REGION, fetch=lambda r: [ITEM], now=lambda: 0.0,
                cache_dir=tmp_path)
    newer = dict(ITEM, retailPrice=2.0)
    later = 25 * 3600
    assert load_prices(REGION, fetch=lambda r: [newer], now=lambda: later,
                       cache_dir=tmp_path) == {"X1 LRS Disk": 2.0}


def test_offline_falls_back_to_stale_cache(tmp_path):
    load_prices(REGION, fetch=lambda r: [ITEM], now=lambda: 0.0,
                cache_dir=tmp_path)

    def offline(region):
        raise OSError("no network")
    assert load_prices(REGION, fetch=offline, now=lambda: 25 * 3600,
                       cache_dir=tmp_path) == {"X1 LRS Disk": 1.0}


def test_offline_without_cache_raises(tmp_path):
    def offline(region):
        raise OSError("no network")
    with pytest.raises(OSError):
        load_prices(REGION, fetch=offline, cache_dir=tmp_path)