
import pytest

from src.pricing.public_ip import parse_public_ip_prices
from src.pricing.cache import load_public_ip_prices
from src.rules.unused_ip import check_unused_public_ips


def make_item(
    price=0.005,
    sku="Standard",
    version="IPv4"
):
    return {
        "serviceName": "Virtual Network",
        "type": "Consumption",
        "currencyCode": "USD",
        "unitOfMeasure": "1 Hour",
        "productName": f"{sku} IP Addresses {version}",
        "meterName": f"{version} IP Address",
        "skuName": sku,
        "retailPrice": price,
        "isPrimaryMeterRegion": True
    }


def test_parse_standard_public_ip_price():
    prices = parse_public_ip_prices([
        make_item()
    ])

    assert prices["Standard|IPv4"] == 0.005


def test_parse_ipv6_price():
    prices = parse_public_ip_prices([
        make_item(price=0.004, version="IPv6")
    ])

    assert prices["Standard|IPv6"] == 0.004


def test_ignore_reservation_prices():
    item = make_item()
    item["type"] = "Reservation"

    assert parse_public_ip_prices([item]) == {}


def test_ignore_non_usd_prices():
    item = make_item()
    item["currencyCode"] = "EUR"

    assert parse_public_ip_prices([item]) == {}


# def test_ambiguous_prices_raise_error():
#     with pytest.raises(ValueError):
#         parse_public_ip_prices([
#             make_item(price=0.005),
#             make_item(price=0.006)
#         ])


def test_cache_saves_prices(tmp_path):
    def fake_fetch(region):
        assert region == "westeurope"
        return [make_item()]

    prices = load_public_ip_prices(
        "westeurope",
        fetch=fake_fetch,
        now=lambda: 1000,
        cache_dir=tmp_path
    )

    assert prices["Standard|IPv4"] == 0.005
    assert (tmp_path / "public_ip_prices_westeurope.json").exists()


def test_unused_ip_monthly_cost():
    ips = [{
        "name": "pip-test-01",
        "resourceGroup": "rg-test",
        "location": "westeurope",
        "sku": "Standard",
        "ipVersion": "IPv4",
        "allocation": "Static",
        "tags": {}
    }]

    prices = {
        "westeurope": {
            "Standard|IPv4": 0.005
        }
    }

    findings = check_unused_public_ips(ips, prices)

    assert len(findings) == 1
    assert findings[0].est_monthly_cost_usd == 3.65


def test_missing_price_does_not_invent_cost():
    ips = [{
        "name": "pip-test-02",
        "resourceGroup": "rg-test",
        "location": "westeurope",
        "sku": "Standard",
        "ipVersion": "IPv4",
        "tags": {}
    }]

    findings = check_unused_public_ips(ips, {})

    assert findings[0].est_monthly_cost_usd == 0.0
    assert "pricing unavailable" in findings[0].issue
