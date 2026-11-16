"""Map a managed disk's SKU and size to its Azure billing tier.

Azure bills a disk at the smallest tier that fits its size (sizes are GiB).
Ultra and Premium SSD v2 are billed per provisioned GB/IOPS/throughput
rather than by tier, so they are deliberately unsupported here.
"""

# (tier name, max size in GiB), smallest first.
_STANDARD_HDD = [("S4", 32), ("S6", 64), ("S10", 128), ("S15", 256),
                 ("S20", 512), ("S30", 1024), ("S40", 2048), ("S50", 4096),
                 ("S60", 8192), ("S70", 16384), ("S80", 32767)]
_STANDARD_SSD = [("E1", 4), ("E2", 8), ("E3", 16), ("E4", 32), ("E6", 64),
                 ("E10", 128), ("E15", 256), ("E20", 512), ("E30", 1024),
                 ("E40", 2048), ("E50", 4096), ("E60", 8192),
                 ("E70", 16384), ("E80", 32767)]
_PREMIUM_SSD = [("P1", 4), ("P2", 8), ("P3", 16), ("P4", 32), ("P6", 64),
                ("P10", 128), ("P15", 256), ("P20", 512), ("P30", 1024),
                ("P40", 2048), ("P50", 4096), ("P60", 8192),
                ("P70", 16384), ("P80", 32767)]

# Resource Graph SKU name -> (tier table, redundancy)
_SKUS = {
    "Standard_LRS": (_STANDARD_HDD, "LRS"),
    "StandardSSD_LRS": (_STANDARD_SSD, "LRS"),
    "Premium_LRS": (_PREMIUM_SSD, "LRS"),
    "StandardSSD_ZRS": (_STANDARD_SSD, "ZRS"),
    "Premium_ZRS": (_PREMIUM_SSD, "ZRS"),
}


def disk_tier(sku: str | None, size_gb: int | None) -> tuple[str, str] | None:
    """Return (tier, redundancy), e.g. ("S4", "LRS"), or None if unknown."""
    if sku not in _SKUS or not size_gb or size_gb <= 0:
        return None
    table, redundancy = _SKUS[sku]
    for tier, max_gb in table:
        if size_gb <= max_gb:
            return tier, redundancy
    return None  # larger than the biggest tier


def meter_name(tier: str, redundancy: str) -> str:
    """The name Azure's price list uses, e.g. 'S4 LRS Disk'."""
    return f"{tier} {redundancy} Disk"