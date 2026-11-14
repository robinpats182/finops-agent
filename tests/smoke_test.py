import os
import pytest
from dotenv import load_dotenv

load_dotenv()

REQUIRED = ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_DEPLOYMENT",
            "AZURE_OPENAI_API_VERSION")

pytestmark = pytest.mark.skipif(
    not all(os.environ.get(k) for k in REQUIRED),
    reason="Azure OpenAI env vars not set",
)


def test_complete_returns_text():
    from src.agent.azure_llm import AzureLLM
    out = AzureLLM().complete("You are concise.", "Say hello in five words.")
    assert isinstance(out, str) and out.strip()


def test_respond_works_with_responses_api():
    from src.agent.azure_llm import AzureLLM
    r = AzureLLM().respond("You are concise.",
                           [{"role": "user", "content": "Say hello."}], [])
    assert r.output_text.strip()