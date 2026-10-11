import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

load_dotenv()


class AzureLLM:
    """Azure OpenAI client using Entra ID (your az login), no API key."""

    def __init__(self):
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default",
        )
        self._client = AzureOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            azure_ad_token_provider=token_provider,
            api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        )
        self._deployment = os.environ["AZURE_OPENAI_DEPLOYMENT"]

    def complete(self, system: str, user: str) -> str:
        response = self._client.chat.completions.create(
            model=self._deployment,  # this is the deployment name
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_completion_tokens=1000,
        )
        return response.choices[0].message.content
    
    def respond(self, instructions: str, input_items: list, tools: list):
        return self._client.responses.create(
            model=self._deployment,
            instructions=instructions,
            input=input_items,
            tools=tools,
            max_output_tokens=2000,
        )