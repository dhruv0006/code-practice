"""
Provider-agnostic LLM helper.

Reads config from environment (.env). Supports OpenAI and Azure OpenAI so the same
code works regardless of which one you configured. Copy this file into each problem
folder (or import it) and build on top of it.

Security: keys are read from environment only — never hardcode them.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import AsyncIterator

from dotenv import load_dotenv

load_dotenv()  # load .env from the current working directory

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()


@lru_cache
def _get_client():
    """Create and cache the async client for the configured provider."""
    if LLM_PROVIDER == "azure":
        from openai import AsyncAzureOpenAI

        return AsyncAzureOpenAI(
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        )
    # default: OpenAI
    from openai import AsyncOpenAI

    return AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])


def chat_model() -> str:
    """The model/deployment name to use for chat completions."""
    if LLM_PROVIDER == "azure":
        return os.environ["AZURE_OPENAI_DEPLOYMENT"]
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def embed_model() -> str:
    """The model/deployment name to use for embeddings."""
    if LLM_PROVIDER == "azure":
        return os.environ["AZURE_OPENAI_EMBED_DEPLOYMENT"]
    return os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")


async def complete(
    system: str,
    user: str,
    *,
    temperature: float = 0.2,
    max_tokens: int | None = None,
    json_mode: bool = False,
) -> str:
    """Single-shot chat completion. Returns the assistant's text."""
    client = _get_client()
    kwargs: dict = {
        "model": chat_model(),
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
    }
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    resp = await client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content or ""


async def stream(
    messages: list[dict],
    *,
    temperature: float = 0.2,
) -> AsyncIterator[str]:
    """Stream a chat completion, yielding text chunks as they arrive."""
    client = _get_client()
    response = await client.chat.completions.create(
        model=chat_model(),
        messages=messages,
        temperature=temperature,
        stream=True,
    )
    async for chunk in response:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


async def embed(texts: list[str]) -> list[list[float]]:
    """Return an embedding vector for each input text."""
    client = _get_client()
    resp = await client.embeddings.create(model=embed_model(), input=texts)
    return [item.embedding for item in resp.data]
