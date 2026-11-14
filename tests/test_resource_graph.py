from types import SimpleNamespace
from src.tools import resource_graph


class FakeClient:
    """Pretends to be Azure: returns one page per call."""
    def __init__(self, pages):
        self.pages = pages
        self.calls = []

    def resources(self, request):
        i = len(self.calls)
        self.calls.append(request)
        data, token = self.pages[i]
        return SimpleNamespace(data=data, skip_token=token)


def test_run_query_follows_skip_token(monkeypatch):
    client = FakeClient([
        ([{"n": 1}, {"n": 2}], "token-1"),  # page 1, more to come
        ([{"n": 3}], None),                 # page 2, last page
    ])
    monkeypatch.setattr(resource_graph, "_make_client", lambda: client)
    monkeypatch.setenv("AZURE_SUBSCRIPTION_ID", "sub-123")

    rows = resource_graph.run_query("Resources")

    assert [r["n"] for r in rows] == [1, 2, 3]
    assert client.calls[0].options.top == 1000
    assert client.calls[1].options.skip_token == "token-1"