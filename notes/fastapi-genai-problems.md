# FastAPI + Gen AI — Problem Set

Medium-complexity problems that combine **API building** with **Gen AI**.
Do them in order. Each has: **Goal**, **Requirements**, **What you'll learn**,
**Hints**, **Acceptance criteria**, and **Stretch goals**.

Create a subfolder per problem (e.g. `p1_summarizer/`) and copy `starter/` into it.

Legend: 🟢 = must do, 🔵 = stretch.

---

## Problem 1 — Text Summarization Service 🟢

**Goal:** Build a `POST /summarize` endpoint that takes raw text and returns an
AI-generated summary with a configurable target length.

**Requirements**
- Request body (Pydantic): `text: str`, `max_words: int = 60`, `style: Literal["bullet","paragraph"] = "paragraph"`.
- Validate: `text` must be non-empty and under ~20k characters (reject with 422).
- Call an LLM to summarize according to `style` and `max_words`.
- Response model: `{ "summary": str, "input_chars": int, "model": str }`.
- Load the API key from `.env` (never hardcode).
- Endpoint must be `async`.

**What you'll learn:** Pydantic request/response models, field validation, async
handlers, environment-based secrets, basic prompt design.

**Hints**
- Use `pydantic.BaseModel` and `Field(..., max_length=20000)`.
- Build the prompt from `style` + `max_words`; keep the system prompt separate.
- Return the model name so you can compare providers later.

**Acceptance criteria**
- [ ] `POST /summarize` returns 200 with a valid summary for good input.
- [ ] Empty or oversized text returns 422 (not 500).
- [ ] No secret is hardcoded; key comes from `.env`.
- [ ] `GET /docs` shows correct request/response schemas.

**Stretch** 🔵
- Add `language: str = "en"` and summarize in that language.
- Add a `GET /health` endpoint that verifies the LLM key is configured.

---

## Problem 2 — Structured Data Extraction 🟢

**Goal:** `POST /extract` that turns unstructured text (e.g. an email or invoice blob)
into **validated structured JSON** — the bread-and-butter of AI for data engineers.

**Requirements**
- Input: `text: str` plus optional `fields: list[str]` (which fields to pull).
- Define a target schema, e.g. `Invoice`: `vendor, invoice_number, date, total_amount, currency, line_items[]`.
- Instruct the LLM to return **JSON only**; parse and validate it into the Pydantic model.
- If the model returns invalid JSON, **retry once** with a stricter instruction, then
  fail with a 502 and a helpful error.
- Response: the validated object + a `confidence_notes: str` field.

**What you'll learn:** Structured/JSON output from LLMs, defensive parsing, retry logic,
mapping messy input to typed models — core data-engineering value.

**Hints**
- Ask for JSON matching your schema; include the schema in the prompt.
- Prefer provider "JSON mode" / structured outputs if available; otherwise parse
  `response_text` with `json.loads` inside a try/except.
- Normalize dates and numbers *after* parsing, not in the prompt.

**Acceptance criteria**
- [ ] Valid input returns a fully-typed, validated object.
- [ ] Malformed LLM output triggers exactly one retry before failing gracefully.
- [ ] Numeric `total_amount` is a real number, not a string.
- [ ] Handles missing fields (returns `null`, not a crash).

**Stretch** 🔵
- Accept a user-supplied JSON schema and generate the Pydantic model dynamically.
- Return per-field confidence.

---

## Problem 3 — Streaming Chat Endpoint 🟢

**Goal:** `POST /chat/stream` that streams tokens back to the client as the LLM
generates them (like ChatGPT typing), using Server-Sent Events (SSE).

**Requirements**
- Input: `messages: list[{role, content}]` (a small chat history).
- Stream the assistant response incrementally using `StreamingResponse`.
- Use SSE format (`data: <chunk>\n\n`) or newline-delimited chunks.
- Handle client disconnects cleanly (stop generating).
- Keep an in-memory cap: reject histories longer than N messages (422).

**What you'll learn:** `StreamingResponse`, async generators, SSE, backpressure and
disconnect handling — key for responsive AI UX.

**Hints**
- Your provider's streaming API yields chunks; `yield` them from an `async def` generator.
- Test with `curl -N` to see the stream, or a tiny HTML page with `EventSource`.
- Wrap the generator in try/except to catch `asyncio.CancelledError` on disconnect.

**Acceptance criteria**
- [ ] Response arrives incrementally, not all at once.
- [ ] `curl -N http://localhost:8000/chat/stream ...` shows progressive output.
- [ ] Disconnecting the client stops server-side generation.
- [ ] Oversized history returns 422.

**Stretch** 🔵
- Add a final SSE event with token/usage stats.
- Add a minimal `static/index.html` chat UI consuming the stream.

---

## Problem 4 — Batch CSV Classifier 🟢

**Goal:** Upload a CSV of rows (e.g. support tickets), classify each row with the LLM
(e.g. category + priority), and return/download results. Very close to real ETL+AI work.

**Requirements**
- `POST /classify/batch` accepts a CSV file upload (`multipart/form-data`).
- For each row, call the LLM to assign `category` (from a fixed label set) and `priority`.
- Process rows **concurrently but bounded** (e.g. max 5 in flight) with **retries** on
  transient errors.
- Return a job model; expose `GET /classify/batch/{job_id}` to fetch status/results.
- Run the work in the **background** so the upload call returns quickly.

**What you'll learn:** File upload, `BackgroundTasks`/async task management, bounded
concurrency (`asyncio.Semaphore`), retry with backoff, job status pattern.

**Hints**
- Parse CSV with `csv.DictReader` (stream, don't load 1GB into RAM naively).
- Use an `asyncio.Semaphore(5)` to cap concurrency.
- Store job state in a dict for now (note: not production-safe; that's fine here).
- Constrain the LLM to your label set; validate its output against it.

**Acceptance criteria**
- [ ] Uploading a CSV returns a `job_id` immediately.
- [ ] Polling the job shows progress then final results.
- [ ] Concurrency is capped (verify you don't fire all requests at once).
- [ ] A transient failure on one row is retried, not fatal to the whole job.

**Stretch** 🔵
- Stream results out as a downloadable CSV.
- Add per-row token/cost accounting to the job summary.

---

## Problem 5 — RAG-lite Document Q&A 🟢

**Goal:** Upload documents, embed them, and answer questions grounded in those docs
(Retrieval-Augmented Generation) — the canonical Gen AI app pattern.

**Requirements**
- `POST /docs` accepts text (or a file); chunk it, create **embeddings**, store vectors
  (in-memory list or a local vector DB like Chroma/FAISS).
- `POST /ask` takes a `question`, embeds it, retrieves top-k chunks, and asks the LLM to
  answer **using only the retrieved context**.
- Response includes the `answer` plus the `sources` (which chunks were used).
- If nothing relevant is found, say "I don't know based on the provided documents."

**What you'll learn:** Embeddings, chunking strategy, similarity search, grounding /
citations, prompt design to reduce hallucination.

**Hints**
- Chunk by ~500–1000 characters with slight overlap.
- Cosine similarity for retrieval; `numpy` is enough for a small demo.
- Put retrieved context in the prompt with clear delimiters; instruct "answer only from context".
- Guard against prompt injection inside documents (treat doc text as untrusted).

**Acceptance criteria**
- [ ] Answers are grounded in uploaded docs and cite sources.
- [ ] Out-of-scope questions return an honest "I don't know".
- [ ] Retrieval returns the most relevant chunks (spot-check).
- [ ] Re-uploading docs updates the index.

**Stretch** 🔵
- Swap the in-memory store for Chroma/FAISS or Azure AI Search.
- Add metadata filters (e.g. by document name).

---

## Problem 6 — Cached & Rate-limited LLM Gateway 🟢

**Goal:** Wrap an LLM call behind a gateway endpoint that **caches** identical requests
and **rate-limits** callers — directly about cost and reliability.

**Requirements**
- `POST /generate` proxies a prompt to the LLM.
- **Cache**: identical prompts (same normalized text + params) return the cached result
  without calling the LLM again. Include cache TTL.
- **Rate limit**: cap requests per client (e.g. by API key/header) to N per minute;
  exceed → 429 with `Retry-After`.
- Add a `X-Cache: HIT|MISS` response header and structured logging of latency + tokens.

**What you'll learn:** Middleware/dependencies, caching (hash keys, TTL), rate limiting
algorithms (token bucket / fixed window), observability basics.

**Hints**
- Cache key = hash of `(model, prompt, temperature, max_tokens)`.
- Use a simple in-memory `dict` with timestamps, or `cachetools.TTLCache`.
- Rate limit with a per-client deque of timestamps (sliding window).
- Return `429` + `Retry-After` header when the limit is hit.

**Acceptance criteria**
- [ ] Repeated identical request returns instantly with `X-Cache: HIT`.
- [ ] Exceeding the rate limit returns 429 with `Retry-After`.
- [ ] Logs show per-request latency and token usage.
- [ ] Different prompts / params bypass the cache correctly.

**Stretch** 🔵
- Back the cache with Redis (Azure Cache for Redis) so it survives restarts.
- Add per-key monthly cost budgets.

---

## After you finish

- You'll have covered: validation, async, streaming, file upload, background jobs,
  bounded concurrency, retries, embeddings/RAG, caching, and rate limiting —
  all while using Gen AI. That's a strong medium-level portfolio.
- Next natural step: **tool-calling / agents** and **deploying to Azure**
  (Azure Container Apps or Azure Functions). Ask Copilot when you're ready.
