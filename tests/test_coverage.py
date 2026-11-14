from src.agent import toolbox as tb
from src.agent.llm import FakeLLM
from src.agent.proposal import build_proposal


def test_missing_scans_are_run_by_code(monkeypatch):
    monkeypatch.setattr(tb, "find_unattached_disks", lambda: [])
    monkeypatch.setattr(tb, "find_unattached_public_ips", lambda: [])
    box = tb.ToolBox()
    box.call("scan_unattached_disks", {})          # the model skipped the IP scan
    assert box.missing_scans() == ["scan_unused_public_ips"]
    assert box.run_missing_scans() == []           # code ran it, nothing missing
    assert box.missing_scans() == []


def test_failed_scan_is_reported_as_missing(monkeypatch):
    def boom():
        raise RuntimeError("azure down")
    monkeypatch.setattr(tb, "find_unattached_disks", boom)
    monkeypatch.setattr(tb, "find_unattached_public_ips", lambda: [])
    box = tb.ToolBox()
    assert box.run_missing_scans() == ["scan_unattached_disks"]


def test_clean_result_is_not_claimed_when_coverage_incomplete():
    p = build_proposal([], FakeLLM(), incomplete_scans=["scan_unattached_disks"])
    assert p.summary != "No waste found."
    assert "scan_unattached_disks" in p.summary
    assert p.incomplete_scans == ("scan_unattached_disks",)


def test_warning_is_added_to_summary_when_findings_exist_but_coverage_incomplete():
    from src.rules.models import Finding
    f = Finding("r", "a", "rg", "issue", 1.0, "low", "delete")
    p = build_proposal([f], FakeLLM(), incomplete_scans=["scan_unused_public_ips"])
    assert "scan_unused_public_ips" in p.summary
    assert p.requires_approval