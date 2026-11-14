from src.agent import toolbox as tb


def make_disk(rg):
    return {
        "id": f"/subscriptions/s/resourceGroups/{rg}/providers/Microsoft.Compute/disks/data-disk",
        "name": "data-disk", "resourceGroup": rg,
        "sizeGb": 10, "sku": "Standard_LRS", "tags": None,
    }


def test_same_name_in_different_groups_are_both_kept(monkeypatch):
    disks = [make_disk("rg1"), make_disk("rg2")]
    monkeypatch.setattr(tb, "find_unattached_disks", lambda: disks)
    box = tb.ToolBox()
    box.call("scan_unattached_disks", {})
    assert len(box.findings) == 2


def test_scanning_twice_does_not_double_count(monkeypatch):
    monkeypatch.setattr(tb, "find_unattached_disks", lambda: [make_disk("rg1")])
    box = tb.ToolBox()
    box.call("scan_unattached_disks", {})
    box.call("scan_unattached_disks", {})
    assert len(box.findings) == 1