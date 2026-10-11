from src.agent.azure_llm import AzureLLM
import os
from dotenv import load_dotenv
load_dotenv()
for k in ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_DEPLOYMENT", "AZURE_OPENAI_API_VERSION"):
    print(k, "=", repr(os.environ.get(k)))

endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")

print(AzureLLM().complete("You are concise.", "Say hello in five words."))