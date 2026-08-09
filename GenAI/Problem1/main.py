from datetime import datetime

import sqlite3

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
from typing_extensions import Literal

from llm import Summarizer, GeminiClient
from prompts import summary_prompt

llm_client = GeminiClient()
summary_prompt = summary_prompt.text_summary_prompt()
summarizer = Summarizer(llm_client, summary_prompt)

# --- Global DB variable ---
db = None

def init_db():
    """Call this once at app startup."""
    global db
    db = sqlite3.connect("summarizer.db", check_same_thread=False)  # creates the file if it doesn't exist
    db.row_factory = sqlite3.Row             # makes rows behave like dicts
    db.execute("""
    CREATE TABLE IF NOT EXISTS text_summary (
        req_id INTEGER PRIMARY KEY AUTOINCREMENT,
        input_text TEXT,
        max_words INTEGER,
        style TEXT DEFAULT 'paragraph',
        llm_summary_text TEXT,
        creation_timestamp TIMESTAMP,
        updation_timestamp TIMESTAMP
    );
    """)
    db.commit()

app = FastAPI(
    title="Text Summarizer API",
    description="AI-powered text summarization platform"
)


@app.on_event("startup")
def on_startup():
    init_db()

class TextInputRequest(BaseModel):
    input_text: str = Field(..., min_length=1, max_length=20_000, description='The text to be summarized. Must be between 1 and 20,000 characters.')
    max_words: int = Field(..., gt=0, le=1000, description='The maximum number of words for the summary. Must be a positive integer not exceeding 1000.')
    style: Optional[Literal['paragraph', 'bullet_points']] = 'paragraph'

@app.post("/api/summarize", status_code=201)
def summarize_text(request: TextInputRequest):
    creation_timestamp = datetime.now()

    # Call the LLM to generate the summary
    summary = summarizer.summarize(
        request.input_text, request.max_words, request.style
    )

    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO text_summary
            (input_text, max_words, style, llm_summary_text, creation_timestamp)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            request.input_text,
            request.max_words,
            request.style,
            summary,
            creation_timestamp,
        ),
    )
    db.commit()
    req_id = cursor.lastrowid

    return {"req_id": req_id, "summary": summary}

@app.get("/api/summarize")
def list_summaries():
    rows = db.execute("SELECT * FROM text_summary").fetchall()
    return [dict(r) for r in rows]

@app.get("/api/summarize/{req_id}")
def get_summary(req_id: int):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM text_summary WHERE req_id = ?", (req_id,))
    row = cursor.fetchone()
    if row is None:
        return JSONResponse(content={"message": "Summary not found."}, status_code=404)
    return JSONResponse(content=dict(row), status_code=200)




