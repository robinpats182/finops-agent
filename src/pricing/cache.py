"""Cache parsed prices on disk so we don't call the API on every run."""
import json
import time
from pathlib import Path

from src.pricing.client import fetch_disk_items
from src.pricing.retail_prices import parse_disk_prices
from src.pricing.client import fetch_public_ip_items
from src.pricing.public_ip import parse_public_ip_prices

CACHE_DIR = Path(".cache")
MAX_AGE_HOURS = 24


def load_prices(region: str, fetch=fetch_disk_items, now=time.time,
                cache_dir: Path = CACHE_DIR,
                max_age_hours: float = MAX_AGE_HOURS) -> dict[str, float]:
    path = cache_dir / f"disk_prices_{region}.json"
    cached = None
    if path.exists():
        try:
            cached = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            cached = None                      # corrupt cache: ignore it
    if cached and now() - cached["fetched_at"] < max_age_hours * 3600:
        return cached["prices"]                # fresh enough, no network

    try:
        prices = parse_disk_prices(fetch(region))
    except Exception:
        if cached:
            return cached["prices"]            # offline: stale beats nothing
        raise
    cache_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"fetched_at": now(), "prices": prices}),
                    encoding="utf-8")
    return prices

def prices_for_disks(disks: list[dict], loader=load_prices) -> dict[str, dict]:
    """Prices per region for the disks given. A failed lookup is skipped,
    so those disks fall back to a flagged estimate instead of crashing."""
    out: dict[str, dict] = {}
    regions = {(d.get("location") or "").lower() for d in disks} - {""}
    for region in regions:
        try:
            out[region] = loader(region)
        except Exception:
            pass
    return out


def load_public_ip_prices(
    region: str,
    fetch=fetch_public_ip_items,
    now=time.time,
    cache_dir: Path = CACHE_DIR,
    max_age_hours: float = MAX_AGE_HOURS
) -> dict[str, float]:

    path = cache_dir / f"public_ip_prices_{region}.json"

    cached = None

    if path.exists():
        try:
            cached = json.loads(
                path.read_text(encoding="utf-8")
            )
        except (OSError, ValueError):
            cached = None

    if (
        cached
        and now() - cached["fetched_at"] < max_age_hours * 3600
    ):
        return cached["prices"]

    try:
        prices = parse_public_ip_prices(fetch(region))

    except Exception:
        if cached:
            return cached["prices"]
        raise

    cache_dir.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps({
            "fetched_at": now(),
            "prices": prices
        }),
        encoding="utf-8"
    )

    return prices


def prices_for_public_ips(
    ips: list[dict],
    loader=load_public_ip_prices
) -> dict[str, dict[str, float]]:
    """Load prices once per region."""

    out = {}

    regions = {
        (ip.get("location") or "").lower()
        for ip in ips
    } - {""}

    for region in regions:
        try:
            out[region] = loader(region)
        except Exception:
            pass

    return out
