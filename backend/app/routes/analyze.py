import base64
import json

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse

from app.core.config import MAX_TEXT_CHARS
from app.utils.file_types import (
    FILE_TYPES, IMAGE_EXTENSIONS, TABULAR_EXTENSIONS,
    TEXT_EXTENSIONS, SUGGESTED_QUESTIONS,
)
from app.parsers.csv_parser    import parse_csv
from app.parsers.excel_parser  import parse_excel
from app.parsers.json_parser   import parse_json
from app.parsers.pdf_parser    import parse_pdf
from app.parsers.docx_parser   import parse_docx
from app.services.analytics_engine import build_summary
from app.services.chart_generator  import generate_chart
from app.services.prompts          import build_analysis_prompt, ANALYSIS_SYSTEM
from app.services.ollama_client    import ollama_stream, ollama_vision

router = APIRouter(prefix="/api")

MAX_ROWS_IN_META = 500   # cap rows sent to frontend to avoid huge payload


@router.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    filename  = file.filename or "unknown"
    ext       = filename.rsplit(".", 1)[-1].lower() if "." in filename else "unknown"
    meta      = FILE_TYPES.get(
        ext, {"label": ext.upper(), "icon": "📄", "color": "#6b7280", "category": "unknown"}
    )
    file_info = {"name": filename, "ext": ext, "size": 0, **meta}

    raw_bytes = await file.read()
    file_info["size"] = len(raw_bytes)

    raw_text  = ""
    summary   = None
    rows      = None
    image_b64 = None
    chart_b64 = None

    # ── Parse ────────────────────────────────────────────────────────────────
    try:
        if ext in IMAGE_EXTENSIONS:
            image_b64 = base64.b64encode(raw_bytes).decode()

        elif ext == "pdf":
            raw_text = parse_pdf(raw_bytes) or "[PDF parse failed — pip install pypdf]"

        elif ext in ("docx", "doc"):
            raw_text = parse_docx(raw_bytes) or "[Word parse failed — pip install python-docx]"

        elif ext in ("xlsx", "xls"):
            headers, rows = parse_excel(raw_bytes)
            if headers and rows:
                summary   = build_summary(headers, rows)
                chart_b64 = generate_chart(headers, rows)
            else:
                raw_text = "[Excel parse failed — pip install openpyxl]"

        elif ext in {"csv", "tsv"}:
            raw_text  = raw_bytes.decode("utf-8", errors="replace")
            delimiter = "\t" if ext == "tsv" else ","
            headers, rows = parse_csv(raw_text, delimiter)
            if headers and rows:
                summary   = build_summary(headers, rows)
                chart_b64 = generate_chart(headers, rows)

        elif ext == "json":
            raw_text = raw_bytes.decode("utf-8", errors="replace")
            h, r = parse_json(raw_text)
            if h and r:
                rows, summary = r, build_summary(h, r)
                chart_b64     = generate_chart(h, r)

        elif ext in TEXT_EXTENSIONS or meta["category"] in ("text", "code", "data"):
            raw_text = raw_bytes.decode("utf-8", errors="replace")

        else:
            raw_text = raw_bytes.decode("utf-8", errors="replace")

    except Exception as e:
        raw_text = f"[Parse error: {e}]"

    if raw_text and len(raw_text) > MAX_TEXT_CHARS:
        raw_text = raw_text[:MAX_TEXT_CHARS] + "\n\n[... truncated ...]"

    prompt    = build_analysis_prompt(file_info, raw_text, summary, rows)
    category  = meta.get("category", "unknown")
    suggested = SUGGESTED_QUESTIONS.get(category, SUGGESTED_QUESTIONS["unknown"])

    # Cap rows sent to frontend — full rows kept in session via frontend state
    rows_for_meta = rows[:MAX_ROWS_IN_META] if rows else None

    # ── Metadata packet — sent FIRST so UI renders instantly ─────────────────
    def make_meta_packet():
        return json.dumps({
            "type":                "meta",
            "file_info":           file_info,
            "structured_summary":  summary,
            "rows":                rows_for_meta,
            "raw_text":            raw_text[:3000] if raw_text else None,
            "suggested_questions": suggested,
            "model_used":          "vision" if image_b64 else "text",
            "chart_b64":           chart_b64,
        }, default=str)   # default=str handles any non-serializable values

    SSE_HEADERS = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}

    # ── Image path ───────────────────────────────────────────────────────────
    if image_b64:
        try:
            insight = await ollama_vision(prompt, image_b64)
        except Exception as e:
            insight = f"Vision analysis failed: {e}"

        async def image_stream():
            yield f"data: {make_meta_packet()}\n\n"
            yield f"data: {json.dumps({'type': 'token', 'token': insight})}\n\n"
            yield 'data: {"type": "done"}\n\n'

        return StreamingResponse(image_stream(), media_type="text/event-stream", headers=SSE_HEADERS)

    # ── Text/tabular path — stream tokens ────────────────────────────────────
    messages = [
        {"role": "system", "content": ANALYSIS_SYSTEM},
        {"role": "user",   "content": prompt},
    ]

    async def analysis_stream():
        try:
            yield f"data: {make_meta_packet()}\n\n"
            async for token in ollama_stream(messages):
                yield f"data: {json.dumps({'type': 'token', 'token': token})}\n\n"
            yield 'data: {"type": "done"}\n\n'
        except Exception as e:
            yield f"data: {json.dumps({'type': 'token', 'token': f'[Error: {e}]'})}\n\n"
            yield 'data: {"type": "done"}\n\n'

    return StreamingResponse(analysis_stream(), media_type="text/event-stream", headers=SSE_HEADERS)