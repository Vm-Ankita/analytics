"""
File analysis endpoint.

Flow:
1. Receive uploaded file
2. Detect file type
3. Parse content
4. Compute statistics + chart
5. Send metadata to frontend
6. Stream AI insights
"""

import base64
import json

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse

from app.core.config import MAX_TEXT_CHARS
from app.utils.file_types import (
    FILE_TYPES,
    IMAGE_EXTENSIONS,
    TEXT_EXTENSIONS,
    SUGGESTED_QUESTIONS,
)

# parsers
from app.parsers.csv_parser import parse_csv
from app.parsers.excel_parser import parse_excel
from app.parsers.json_parser import parse_json
from app.parsers.pdf_parser import parse_pdf
from app.parsers.docx_parser import parse_docx

# services
from app.services.analytics_engine import build_summary
from app.services.chart_generator import generate_chart
from app.services.prompts import build_analysis_prompt, ANALYSIS_SYSTEM
from app.services.ollama_client import ollama_stream, ollama_vision


router = APIRouter(prefix="/api")

# Limit rows sent to frontend to avoid huge payload
MAX_ROWS_IN_META = 500

# SSE headers (disable buffering)
SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
}


# ----------------------------------------------------
# Helper: format SSE event
# ----------------------------------------------------

def sse(data: dict) -> str:
    """Format server-sent event."""
    return f"data: {json.dumps(data, default=str)}\n\n"


# ----------------------------------------------------
# MAIN ROUTE
# ----------------------------------------------------

@router.post("/analyze")
async def analyze(file: UploadFile = File(...)):

    # ------------------------------
    # Basic file info
    # ------------------------------

    filename = file.filename or "unknown"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "unknown"

    meta = FILE_TYPES.get(
        ext,
        {"label": ext.upper(), "icon": "📄", "color": "#6b7280", "category": "unknown"},
    )

    file_info = {
        "name": filename,
        "ext": ext,
        "size": 0,
        **meta,
    }

    raw_bytes = await file.read()
    file_info["size"] = len(raw_bytes)

    raw_text = ""
    summary = None
    rows = None
    chart_b64 = None
    image_b64 = None

    # ------------------------------
    # Parse file
    # ------------------------------

    try:

        if ext in IMAGE_EXTENSIONS:
            image_b64 = base64.b64encode(raw_bytes).decode()

        elif ext == "pdf":
            raw_text = parse_pdf(raw_bytes)

        elif ext in ("docx", "doc"):
            raw_text = parse_docx(raw_bytes)

        elif ext in ("xlsx", "xls"):
            headers, rows = parse_excel(raw_bytes)

            if headers and rows:
                summary = build_summary(headers, rows)
                chart_b64 = generate_chart(headers, rows)

        elif ext in {"csv", "tsv"}:
            raw_text = raw_bytes.decode("utf-8", errors="replace")

            delimiter = "\t" if ext == "tsv" else ","
            headers, rows = parse_csv(raw_text, delimiter)

            if headers and rows:
                summary = build_summary(headers, rows)
                chart_b64 = generate_chart(headers, rows)

        elif ext == "json":
            raw_text = raw_bytes.decode("utf-8", errors="replace")

            headers, rows = parse_json(raw_text)

            if headers and rows:
                summary = build_summary(headers, rows)
                chart_b64 = generate_chart(headers, rows)

        elif ext in TEXT_EXTENSIONS:
            raw_text = raw_bytes.decode("utf-8", errors="replace")

        else:
            raw_text = raw_bytes.decode("utf-8", errors="replace")

    except Exception as e:
        raw_text = f"[Parse error: {e}]"

    # ------------------------------
    # Truncate very large text
    # ------------------------------

    if raw_text and len(raw_text) > MAX_TEXT_CHARS:
        raw_text = raw_text[:MAX_TEXT_CHARS] + "\n\n[... truncated ...]"

    # ------------------------------
    # Build AI prompt
    # ------------------------------

    prompt = build_analysis_prompt(file_info, raw_text, summary, rows)

    category = meta.get("category", "unknown")
    suggested = SUGGESTED_QUESTIONS.get(category, SUGGESTED_QUESTIONS["unknown"])

    rows_for_meta = rows[:MAX_ROWS_IN_META] if rows else None

    # ------------------------------
    # Metadata packet (sent first)
    # ------------------------------

    def build_meta():

        return {
            "type": "meta",
            "file_info": file_info,
            "structured_summary": summary,
            "rows": rows_for_meta,
            "raw_text": raw_text[:3000] if raw_text else None,
            "suggested_questions": suggested,
            "model_used": "vision" if image_b64 else "text",
            "chart_b64": chart_b64,
        }

    # ------------------------------------------------
    # Image analysis path
    # ------------------------------------------------

    if image_b64:

        async def image_stream():

            yield sse(build_meta())

            try:
                insight = await ollama_vision(prompt, image_b64)
            except Exception as e:
                insight = f"Vision analysis failed: {e}"

            yield sse({"type": "token", "token": insight})
            yield sse({"type": "done"})

        return StreamingResponse(image_stream(), media_type="text/event-stream", headers=SSE_HEADERS)

    # ------------------------------------------------
    # Text / data streaming path
    # ------------------------------------------------

    messages = [
        {"role": "system", "content": ANALYSIS_SYSTEM},
        {"role": "user", "content": prompt},
    ]

    async def analysis_stream():

        yield sse(build_meta())

        try:
            async for token in ollama_stream(messages):
                yield sse({"type": "token", "token": token})

        except Exception as e:
            yield sse({"type": "token", "token": f"[Error: {e}]"})

        yield sse({"type": "done"})

    return StreamingResponse(
        analysis_stream(),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )