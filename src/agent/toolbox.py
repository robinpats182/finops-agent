from dataclasses import asdict

from src.tools.resource_graph import (
    list_resources, find_unattached_disks, find_unattached_public_ips,
)
from src.rules.orphan_disk import check_unattached_disks
from src.rules.unused_ip import check_unused_public_ips

EMPTY = {"type": "object", "properties": {}, "required": []}

TOOL_SCHEMAS = [
    {"type": "function", "name": "list_resources",
     "description": "List all resources in the subscription (name, type, resource group).",
     "parameters": EMPTY},
    {"type": "function", "name": "scan_unattached_disks",
     "description": "Find managed disks not attached to any VM, with cost estimates.",
     "parameters": EMPTY},
    {"type": "function", "name": "scan_unused_public_ips",
     "description": "Find public IP addresses not attached to anything, with cost estimates.",
     "parameters": EMPTY},
]

REQUIRED_SCANS = ("scan_unattached_disks", "scan_unused_public_ips")

class ToolBox:
    """Read-only tools. Findings are collected here, so totals come from code."""

    def __init__(self):
        self._findings = {}
        self._completed = set()

    @property
    def findings(self):
        return list(self._findings.values())

    def _store(self, found):
        for f in found:
            # Resource IDs are globally unique; names are not.
            ident = (f.resource_id or f"{f.resource_group}/{f.resource_name}").lower()
            self._findings[(f.rule, ident)] = f
        return [asdict(f) for f in found]

    def _run_scan(self, name):
        if name == "scan_unattached_disks":
            return check_unattached_disks(find_unattached_disks())
        return check_unused_public_ips(find_unattached_public_ips())

    def missing_scans(self):
        """Required scans that have not completed successfully."""
        return [s for s in REQUIRED_SCANS if s not in self._completed]

    def run_missing_scans(self):
        """Code, not the model, guarantees coverage. Returns what is still missing."""
        for name in self.missing_scans():
            self.call(name, {})
        return self.missing_scans()

    def call(self, name: str, args: dict):
        try:
            if name == "list_resources":
                return [{k: r[k] for k in ("name", "type", "resourceGroup")}
                        for r in list_resources()]
            if name in REQUIRED_SCANS:
                result = self._store(self._run_scan(name))
                self._completed.add(name)   # only after it fully succeeded
                return result
            return {"error": f"unknown tool: {name}"}
        except Exception as e:  # return errors to the model instead of crashing
            return {"error": f"{type(e).__name__}: {e}"}