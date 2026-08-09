import os
import httpx
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class OpenAIClient:
    """Client for OpenAI Chat Completion API."""

    def __init__(self, model="gpt-4o-mini"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
        self.client = OpenAI(
            api_key=api_key,
            http_client=httpx.Client(verify=False)
        )
        self.model = model

    def chat_completion(self, messages, temperature=None, max_tokens=None):
        kwargs = {"model": self.model, "messages": messages}
        if temperature is not None:
            kwargs["temperature"] = temperature
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens

        response = self.client.chat.completions.create(**kwargs)
        return response

    def extract_response_text(self, response):
        return response.choices[0].message.content
