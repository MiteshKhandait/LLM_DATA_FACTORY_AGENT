import json
import os

from dotenv import load_dotenv
from ollama import Client


load_dotenv()


class LLMClient:
    """
    Client used by the application to communicate with the local LLM.
    """

    def __init__(self):
        self.host = os.getenv(
            "OLLAMA_HOST",
            "http://localhost:11434",
        )

        self.model = os.getenv(
            "MODEL_NAME",
            "qwen3-8b-8k",
        )

        self.client = Client(host=self.host)

    def generate(self, prompt: str) -> str:
        """
        Send a prompt to the configured Ollama model
        and return the generated response.
        """

        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.message.content

    def generate_json(self, prompt: str) -> dict:
        """
        Send a prompt and request a JSON response.
        """

        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            format="json",
        )

        content = response.message.content

        try:
            return json.loads(content)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"LLM returned invalid JSON: {content}"
            ) from error


    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ):
        """
        Send a chat request to the model, optionally providing tools.
        """

        return self.client.chat(
            model=self.model,
            messages=messages,
            tools=tools,
        )