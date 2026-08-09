"""
Minimal FastAPI + LLM skeleton.

Copy this whole `starter/` folder into a new problem folder (e.g. `p1_summarizer/`)
and edit it to solve the problem. Run with:

    uvicorn main:app --reload

Then open http://localhost:8000/docs
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

import llm_client

app = FastAPI(title="FastAPI + Gen AI Practice", version="0.1.0")


class EchoRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=20_000)


class EchoResponse(BaseModel):
    reply: str
    model: str


@app.get("/health")
async def health() -> dict:
    """Confirms the app is up and a model is configured."""
    return {"status": "ok", "model": llm_client.chat_model()}


@app.post("/echo", response_model=EchoResponse)
async def echo(req: EchoRequest) -> EchoResponse:
    """Sample endpoint: sends the prompt to the LLM and returns the reply.

    Replace this with the endpoint(s) required by your current problem.
    """
    reply = await llm_client.complete(
        system="You are a concise, helpful assistant.",
        user=req.prompt,
    )
    return EchoResponse(reply=reply, model=llm_client.chat_model())
