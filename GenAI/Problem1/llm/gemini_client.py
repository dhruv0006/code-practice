import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


class GeminiClient:
    """Client for Google Gemini API.

    Mirrors OpenAIClient's interface (chat_completion / extract_response_text)
    so it can be dropped into Summarizer without any other code changes.
    """

    def __init__(self, model="gemini-2.5-flash"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(client_args={"verify": False}),
        )
        self.model = model

    def chat_completion(self, messages, temperature=None, max_tokens=None):
        # Gemini keeps the system prompt separate and uses role "model" (not
        # "assistant"), so translate the OpenAI-style messages accordingly.
        system_instruction = None
        contents = []
        for message in messages:
            role = message["role"]
            content = message["content"]
            if role == "system":
                system_instruction = content
                continue
            gemini_role = "model" if role == "assistant" else "user"
            contents.append(
                types.Content(role=gemini_role, parts=[types.Part(text=content)])
            )

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=config,
        )
        return response

    def extract_response_text(self, response):
        return response.text
