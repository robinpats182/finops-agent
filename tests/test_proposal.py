from src.agent.llm import FakeLLM
from src.agent.proposal import build_proposal
from src.rules.models import Finding


def make_finding(name, cost, risk="medium"):
    return Finding("r", name, "rg", "issue", cost, risk, "delete")


def test_total_is_computed_by_code():
    p = build_proposal([make_finding("a", 1.5), make_finding("b", 2.25)], FakeLLM())
    assert p.total_monthly_savings_usd == 3.75


def test_findings_sorted_by_cost_descending():
    p = build_proposal([make_finding("a", 1.0), make_finding("b", 5.0)], FakeLLM())
    assert [f.resource_name for f in p.findings] == ["b", "a"]


def test_no_findings_needs_no_approval():
    p = build_proposal([], FakeLLM())
    assert p.requires_approval is False
    assert p.summary == "No waste found."


def test_findings_require_approval():
    assert build_proposal([make_finding("a", 1.0)], FakeLLM()).requires_approval