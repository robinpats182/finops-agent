from typing import Protocol


class LLM(Protocol):
    def complete(self, system: str, user: str) -> str: ...


class FakeLLM:
    """Deterministic stand-in for tests and offline demos."""

    def complete(self, system: str, user: str) -> str:
        return "Fake summary: review the findings below."