"""Fetch managed-disk prices from the public Azure Retail Prices API."""
import json
import re
import urllib.parse
import urllib.request
from urllib.parse import urlparse


BASE_URL = "https://prices.azure.com/api/retail/prices"
MAX_PAGES = 20          # safety stop, same idea as the agent's step limit
TIMEOUT_SECONDS = 30

def build_url(region: str) -> str:
    # The region goes into an OData filter, so allow only plain region names.
    if not re.fullmatch(r"[a-z0-9]+", region):
        raise ValueError(f"invalid region: {region!r}")
    flt = (f"serviceName eq 'Storage' and armRegionName eq '{region}' "
           "and contains(productName,'Managed Disks')")
    return BASE_URL + "?" + urllib.parse.urlencode(
        {"$filter": flt}, quote_via=urllib.parse.quote)


def _http_get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as resp:
        return json.load(resp)


def fetch_disk_items(region: str, get_json=_http_get_json) -> list[dict]:
    """Return all price items for the region, following NextPageLink."""
    url = build_url(region)
    items: list[dict] = []
    for _ in range(MAX_PAGES):
        page = get_json(url)
        items.extend(page.get("Items", []))
        url = page.get("NextPageLink")
        if not url:
            return items
        # Only follow links that stay on the official price host.
        if not url.startswith("https://prices.azure.com/"):
            raise ValueError(f"unexpected NextPageLink host: {url}")
    raise RuntimeError("Retail Prices API returned too many pages; stopping.")



def build_public_ip_url(region: str) -> str:
    if not re.fullmatch(r"[a-z0-9]+", region):
        raise ValueError(f"invalid region: {region!r}")

    flt = (
        f"armRegionName eq '{region}' "
        "and serviceName eq 'Virtual Network' "
        "and contains(meterName,'IP Address')"
    )

    return BASE_URL + "?" + urllib.parse.urlencode(
        {"$filter": flt},
        quote_via=urllib.parse.quote
    )


def fetch_public_ip_items(
    region: str,
    get_json=_http_get_json
) -> list[dict]:
    """Fetch Public IP pricing records, following pagination."""

    url = build_public_ip_url(region)
    items = []

    for _ in range(MAX_PAGES):
        page = get_json(url)
        print("API records returned:", len(page.get("Items", [])))

        items.extend(page.get("Items", []))

        url = page.get("NextPageLink")

        if not url:
            return items

        # Allow the official host, including its optional :443 port.
        parsed = urlparse(url)

        if (
            parsed.scheme != "https"
            or parsed.hostname != "prices.azure.com"
            or parsed.username
            or parsed.password
        ):
            raise ValueError(
                f"unexpected NextPageLink host: {url}"
            )

    raise RuntimeError(
        "Retail Prices API returned too many pages; stopping."
    )
