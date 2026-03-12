import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.chat import AskRequest
from app.services.ollama_client import ollama_stream, ollama_vision

router = APIRouter(prefix="/api")

# ── System prompts ────────────────────────────────────────────────────────────

ANALYSIS_SYSTEM = (
    "You are an expert data analyst. "
    "Use markdown: ## headers and bullet points. "
    "Be specific with numbers. Keep response under 350 words."
)

QA_SYSTEM = """You are a precise data analyst assistant.

RULES:
1. The user's data is shown in the DATA TABLE below — use it directly.
2. For specific lookups (a person's name, ID, value) — find the exact row and quote it.
3. For aggregates (count, average, total) — compute from all visible rows.
4. If a name/value is NOT in the table, say: "I couldn't find [X] in the dataset."
5. Never guess or hallucinate. Be concise and factual.
6. Cite the exact cell value when answering specific lookups."""


# ── Row search ────────────────────────────────────────────────────────────────

STOP_WORDS = {
    'what', 'is', 'the', 'a', 'an', 'of', 'in', 'for', 'and', 'or',
    'are', 'was', 'were', 'has', 'have', 'does', 'do', 'tell', 'me',
    'show', 'find', 'give', 'list', 'all', 'which', 'who', 'where',
    'when', 'how', 'many', 'much', 'their', 'his', 'her', 'its', 'my',
    'your', 'our', 'this', 'that', 'these', 'those', 'from', 'with',
    'about', 'get', 'can', 'you', 'please', 'name', 'value', 's',
}


def extract_search_terms(question: str) -> list[str]:
    """Pull meaningful keywords from the question."""
    words = question.lower().replace("'s", "").replace("?", "").replace(",", "").split()
    return [w for w in words if w not in STOP_WORDS and len(w) >= 2]


def search_rows(question: str, rows: list, headers: list, max_rows: int = 50) -> list:
    """
    Score every row by how many search terms appear in its cell values.
    Returns top-scoring rows so the LLM always sees the relevant data.
    """
    if not rows:
        return []

    terms = extract_search_terms(question)
    if not terms:
        return rows[:max_rows]

    scored = []
    for row in rows:
        row_text = " ".join(str(v).lower() for v in row.values())
        # Exact substring match per term
        score = sum(1 for t in terms if t in row_text)
        if score > 0:
            scored.append((score, row))

    if scored:
        scored.sort(key=lambda x: -x[0])
        return [r for _, r in scored[:max_rows]]

    # No keyword match — return first rows so LLM has something
    return rows[:max_rows]


# ── Context builder ───────────────────────────────────────────────────────────

def build_context(req: AskRequest) -> str:
    """
    Builds the full context string:
      1. Brief file summary
      2. Relevant data rows as a markdown table (smart-searched)
      3. The question
    """
    parts = []

    # File summary line
    parts.append(req.file_context.split("\n\nAnalysis:")[0])  # strip old AI analysis

    # Smart-searched data table
    if req.rows and req.headers:
        relevant = search_rows(req.question, req.rows, req.headers, max_rows=60)

        parts.append(
            f"\n\n## DATA TABLE — {len(relevant)} rows "
            f"(searched from {len(req.rows)} total)\n"
        )
        # Markdown table
        parts.append("| " + " | ".join(req.headers) + " |")
        parts.append("|" + " --- |" * len(req.headers))
        for row in relevant:
            vals = [str(row.get(h, "")).replace("|", "\\|") for h in req.headers]
            parts.append("| " + " | ".join(vals) + " |")

    parts.append(f"\n\n## QUESTION\n{req.question}")
    return "\n".join(parts)


# ── Route ─────────────────────────────────────────────────────────────────────

@router.post("/ask")
async def ask(req: AskRequest):
    # Vision Q&A (images) — non-streaming
    if req.image_base64:
        answer = await ollama_vision(
            QA_SYSTEM + f"\n\nQuestion: {req.question}", req.image_base64
        )
        return {"answer": answer}

    context = build_context(req)

    # Build message list: system → history → current question
    messages = [{"role": "system", "content": QA_SYSTEM}]

    # Last 4 history turns for multi-turn context
    for msg in req.conversation[-4:]:
        if msg.role in ("user", "assistant") and msg.content:
            messages.append({"role": msg.role, "content": msg.content})

    # Current question with full data context
    messages.append({"role": "user", "content": context})

    # Stream tokens back to frontend
    async def event_stream():
        async for token in ollama_stream(messages):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )