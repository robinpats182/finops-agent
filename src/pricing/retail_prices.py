"""Turn Azure Retail Prices API items into a {meterName: monthly price} table."""


def parse_disk_prices(items: list[dict]) -> dict[str, float]:
    """Keep only monthly per-disk prices, keyed by meter name.

    Skipped on purpose:
    - per-transaction meters ("... Disk Operations", unit "10K")
    - reservations and other non-Consumption price types
    - any meter whose items disagree on price. We would rather fall back
      to a flagged estimate than guess which price is right.
    """
    seen: dict[str, set[float]] = {}
    for it in items:
        name = it.get("meterName", "")
        if (it.get("type") != "Consumption"
                or it.get("unitOfMeasure") != "1/Month"
                or "Managed Disks" not in it.get("productName", "")
                or not name.endswith(" Disk")):
            continue
        seen.setdefault(name, set()).add(float(it["retailPrice"]))
    return {name: next(iter(p)) for name, p in seen.items() if len(p) == 1}