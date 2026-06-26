"""
api.py — FastAPI Gateway | Heuristic OS V3.1
AquaHeuristic Platform

Changes from prototype:
  - /explain now has try/except with granular HTTP status codes
  - Structured logging on every request (level, latency, confidence)
  - Input validation via Pydantic field_validator
  - Typed response model (ExplainResponse)
  - /health endpoint for Render health checks
  - CORS middleware driven by environment variable
  - processing_time_ms added to response payload
"""

from __future__ import annotations

import logging
import os
import time

import uvicorn
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

from brain import ConceptReport, process_concept

# ---------------------------------------------------------------------------
# Logging — structured, timestamp-prefixed
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App bootstrap
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Frontend UI  (primary brand colour: #5F57FF)
# ---------------------------------------------------------------------------
UI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Heuristic OS — V3.1</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    :root { --brand: #5F57FF; --brand-dim: #3d37cc; }
    body  { background-color: #0b1016; color: #88a7c2; font-family: monospace; }
    .panel { background-color: #121820; border: 1px solid #2a3547; border-radius: 6px; }
    .btn-primary {
      background-color: var(--brand);
      transition: background-color .2s;
    }
    .btn-primary:hover { background-color: var(--brand-dim); }
    .status-dot {
      display: inline-block; width: 8px; height: 8px;
      border-radius: 50%; background: #22c55e; margin-right: 6px;
    }
  </style>
</head>
<body class="p-10">
  <header class="mb-8 flex items-center gap-3">
    <span class="status-dot"></span>
    <h1 class="text-2xl text-white font-bold tracking-widest">HEURISTIC_OS <span style="color:var(--brand)">V3.1</span></h1>
  </header>

  <div class="grid grid-cols-2 gap-6">
    <!-- Input panel -->
    <div class="panel p-6">
      <label class="block text-xs text-gray-500 mb-2 uppercase tracking-widest">Input Sequence</label>
      <textarea id="textarea"
        class="w-full h-36 bg-black border border-gray-700 rounded p-3 text-white text-sm resize-none focus:outline-none focus:border-indigo-500"
        placeholder="Enter concept or sequence…"></textarea>

      <button onclick="runAnalysis()"
        class="btn-primary w-full mt-4 py-3 text-white font-bold rounded tracking-widest text-sm">
        INITIALIZE_ANALYSIS
      </button>

      <div id="error-box" class="hidden mt-3 text-red-400 text-xs bg-red-900/20 p-3 rounded"></div>
    </div>

    <!-- Output panel -->
    <div class="panel p-6">
      <div id="telemetry" class="text-xs mb-4 text-gray-500 tracking-widest">
        CONFIDENCE: [N/A] | PROC_TIME: [—] | STATUS: IDLE
      </div>
      <pre id="output-box" class="text-sm text-gray-300 whitespace-pre-wrap leading-relaxed">System ready…</pre>
    </div>
  </div>

  <script>
    async function runAnalysis() {
      const input   = document.getElementById('textarea').value.trim();
      const output  = document.getElementById('output-box');
      const tele    = document.getElementById('telemetry');
      const errBox  = document.getElementById('error-box');

      errBox.classList.add('hidden');
      errBox.textContent = '';

      if (!input) {
        errBox.textContent = 'ERROR: Input sequence cannot be empty.';
        errBox.classList.remove('hidden');
        return;
      }

      output.textContent = 'Processing…';
      const t0 = performance.now();

      try {
        const res = await fetch('/explain', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: input })
        });

        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: res.statusText }));
          throw new Error(`${res.status}: ${err.detail || 'Unknown error'}`);
        }

        const data = await res.json();
        const clientMs = (performance.now() - t0).toFixed(0);

        output.textContent = data.result;
        tele.textContent =
          `CONFIDENCE: [${data.confidence}%] | SERVER_TIME: [${data.processing_time_ms}ms] | CLIENT_RTT: [${clientMs}ms] | STATUS: OK`;

      } catch (e) {
        output.textContent = '';
        errBox.textContent = 'ERROR: ' + e.message;
        errBox.classList.remove('hidden');
        tele.textContent = 'CONFIDENCE: [—] | STATUS: FAILED';
      }
    }

    // Allow Ctrl+Enter to submit
    document.addEventListener('DOMContentLoaded', () => {
      document.getElementById('textarea').addEventListener('keydown', e => {
        if (e.ctrlKey && e.key === 'Enter') runAnalysis();
      });
    });
  </script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/")
async def root() -> Response:
    return Response(content=UI_HTML, media_type="text/html")


@app.get("/health")
async def health() -> dict[str, str]:
    """Render health-check probe endpoint."""
    return {"status": "ok", "version": "3.1.0"}


@app.post("/explain", response_model=ExplainResponse)
async def explain_text(data: RequestData) -> ExplainResponse:
    """
    Accepts a text concept and returns a structured heuristic analysis.

    - 422  Validation error (empty input, schema mismatch)
    - 500  Internal error from brain.py
    """
    t0 = time.perf_counter()
    logger.info("POST /explain | input_length=%d", len(data.text))

    try:
        result_data: ConceptReport = process_concept(data.text)

    except ValueError as exc:
        # Empty / invalid input that slipped past Pydantic
        logger.warning("POST /explain | 422 | %s", exc)
        raise HTTPException(status_code=422, detail=str(exc))

    except Exception as exc:
        # Catch-all: log full traceback, return safe message to client
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


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, log_level="info", reload=False)