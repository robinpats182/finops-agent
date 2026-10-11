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


class ToolBox:
    """Read-only tools. Findings are collected here, so totals come from code."""

    def __init__(self):
        self._findings = {}

    @property
    def findings(self):
        return list(self._findings.values())

    def _store(self, found):
        for f in found:
            self._findings[(f.rule, f.resource_name)] = f
        return [asdict(f) for f in found]

    def call(self, name: str, args: dict):
        try:
            if name == "list_resources":
                return [{k: r[k] for k in ("name", "type", "resourceGroup")}
                        for r in list_resources()]
            if name == "scan_unattached_disks":
                return self._store(check_unattached_disks(find_unattached_disks()))
            if name == "scan_unused_public_ips":
                return self._store(check_unused_public_ips(find_unattached_public_ips()))
            return {"error": f"unknown tool: {name}"}
        except Exception as e:  # return errors to the model instead of crashing
            return {"error": f"{type(e).__name__}: {e}"}