"""
api.py — FastAPI Gateway | Heuristic OS V3.1
AquaHeuristic Platform
"""

from __future__ import annotations

import logging
import os
import time

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator

from brain import ConceptReport, process_concept

# ── LOGGING ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── APP ────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Heuristic OS",
    version="3.1.0",
    description="Strategic Heuristic Analysis Engine — AquaHeuristic Platform",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve everything inside /static at the /static URL path
app.mount("/static", StaticFiles(directory="static"), name="static")

# ── SCHEMAS ────────────────────────────────────────────────────────────────
class RequestData(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("'text' must not be empty or whitespace.")
        return v.strip()


class ExplainResponse(BaseModel):
    result: str
    confidence: float
    processing_time_ms: float


# ── ROUTES ─────────────────────────────────────────────────────────────────
@app.get("/")
async def root() -> FileResponse:
    """Serve the Heuristic OS command center UI."""
    return FileResponse("static/index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    """Render health-check probe — must return 200 for deployment to succeed."""
    return {"status": "ok", "version": "3.1.0"}


@app.post("/explain", response_model=ExplainResponse)
async def explain_text(data: RequestData) -> ExplainResponse:
    """
    Accepts a text concept and returns a structured heuristic analysis.

    Errors:
        422 — empty / invalid input
        500 — internal processing failure
    """
    t0 = time.perf_counter()
    logger.info("POST /explain | input_length=%d", len(data.text))

    try:
        result_data: ConceptReport = process_concept(data.text)

    except ValueError as exc:
        logger.warning("POST /explain | 422 | %s", exc)
        raise HTTPException(status_code=422, detail=str(exc))

    except Exception as exc:
        logger.error("POST /explain | 500 | %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Heuristic processing failed. Check server logs for details.",
        )

    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
    logger.info(
        "POST /explain | 200 | confidence=%.1f | time=%.1fms",
        result_data["confidence"],
        elapsed_ms,
    )

    return ExplainResponse(
        result=result_data["text"],
        confidence=result_data["confidence"],
        processing_time_ms=elapsed_ms,
    )


# ── ENTRYPOINT ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, log_level="info", reload=False)