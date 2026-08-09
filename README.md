# FastAPI + Gen AI Practice Kit

A self-paced practice kit for a **data engineer** learning to build **APIs** that
**leverage Generative AI**. You know FastAPI basics — these problems push you into
medium-complexity, real-world territory.

## How to use this with Copilot (after reopening VS Code)

When you restart VS Code, you can prompt Copilot like this:

> "Refer to `notes/copilot-context.md` and help me with Problem 3 in
> `notes/fastapi-genai-problems.md`."

or

> "I finished Problem 2. Review my code against the acceptance criteria in the notes."

Copilot will read the notes and continue coaching you.

## Folder structure

```
practice/
├── README.md                       <- you are here
├── requirements.txt                <- Python dependencies
├── .env.example                    <- copy to .env and fill in keys
├── notes/
│   ├── copilot-context.md          <- persistent context: who you are, goals, rules
│   ├── setup-guide.md              <- environment + provider setup
│   ├── fastapi-genai-problems.md   <- the graded problem set (start here)
│   └── learning-log.md             <- track what you finished + notes to self
└── starter/
    ├── main.py                     <- minimal FastAPI + LLM skeleton to copy
    └── llm_client.py               <- provider-agnostic LLM helper
```

## Quick start

1. Open `notes/setup-guide.md` and create your virtual environment.
2. Copy `.env.example` to `.env` and add your API key.
3. Read `notes/fastapi-genai-problems.md` and start with **Problem 1**.
4. Use `starter/` as your scaffold for each problem.

## Learning path (recommended order)

| # | Problem                          | Core API skill              | Core AI skill               |
|---|----------------------------------|-----------------------------|-----------------------------|
| 1 | Text Summarization Service       | Pydantic models, async      | Prompting, env-based keys   |
| 2 | Structured Data Extraction       | Response validation         | JSON / structured output    |
| 3 | Streaming Chat Endpoint          | StreamingResponse / SSE     | Token streaming             |
| 4 | Batch CSV Classifier             | File upload, background jobs | Batching, retries           |
| 5 | RAG-lite Doc Q&A                 | Multi-endpoint state        | Embeddings + retrieval      |
| 6 | Cached & Rate-limited LLM Gateway| Middleware, caching         | Cost control                |

Do them in order — each builds on the previous.
