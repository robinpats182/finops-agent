
import re


def parse_public_ip_prices(items: list[dict]) -> dict[str, float]:
    candidates: dict[str, set[float]] = {}

    for item in items:
        if item.get("serviceName") != "Virtual Network":
            continue

        if item.get("type", item.get("priceType")) != "Consumption":
            continue

        if item.get("currencyCode") != "USD":
            continue

        if item.get("unitOfMeasure") != "1 Hour":
            continue

        meter = item.get("meterName", "").lower()
        product = item.get("productName", "").lower()
        sku = item.get("skuName", "")

        if "ip address" not in meter:
            continue

        if sku not in ("Standard", "Basic"):
            continue

        version = (
            "IPv6" if "ipv6" in meter + product
            else "IPv4" if "ipv4" in meter + product
            else "Any"
        )

        price = float(item.get("retailPrice", 0))

        if price <= 0:
            continue

        key = f"{sku}|{version}"
        candidates.setdefault(key, set()).add(price)

    prices = {}

    for key, values in candidates.items():
        if len(values) > 1:
            raise ValueError(
                f"Ambiguous Public IP prices for {key}: {values}"
            )

        prices[key] = next(iter(values))

    return prices
