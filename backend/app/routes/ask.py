import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.chat import AskRequest
from app.services.ollama_client import ollama_stream, ollama_vision

router = APIRouter(prefix="/api")


# ----------------------------------------------------
# Stop words removed from search queries
# ----------------------------------------------------

STOP_WORDS = {
    "what","is","the","a","an","of","in","for","and","or",
    "are","was","were","has","have","does","do","tell",
    "me","show","find","give","list","all","which",
}


# ----------------------------------------------------
# Extract keywords from question
# ----------------------------------------------------

def extract_terms(question: str):

    words = question.lower().replace("?", "").replace(",", "").split()

    return [
        w for w in words
        if w not in STOP_WORDS and len(w) > 2
    ]


# ----------------------------------------------------
# Search relevant rows
# ----------------------------------------------------

def search_rows(question, rows, max_rows=50):

    terms = extract_terms(question)

    if not terms:
        return rows[:max_rows]

    scored = []

    for row in rows:

        row_text = " ".join(str(v).lower() for v in row.values())

        score = sum(1 for t in terms if t in row_text)

        if score > 0:
            scored.append((score, row))

    scored.sort(key=lambda x: -x[0])

    return [r for _, r in scored[:max_rows]] if scored else rows[:max_rows]


# ----------------------------------------------------
# Build context for LLM
# ----------------------------------------------------

def build_context(req: AskRequest):

    parts = []

    parts.append(req.file_context.split("\n\nAnalysis:")[0])

    if req.rows and req.headers:

        relevant = search_rows(req.question, req.rows)

        parts.append("\n\n## DATA TABLE\n")

        parts.append("| " + " | ".join(req.headers) + " |")
        parts.append("|" + " --- |" * len(req.headers))

        for row in relevant:
            values = [str(row.get(h, "")) for h in req.headers]
            parts.append("| " + " | ".join(values) + " |")

    parts.append(f"\n\n## QUESTION\n{req.question}")

    return "\n".join(parts)


# ----------------------------------------------------
# Ask endpoint
# ----------------------------------------------------

@router.post("/ask")
async def ask(req: AskRequest):

    # Vision question
    if req.image_base64:

        answer = await ollama_vision(
            f"Analyze image and answer: {req.question}",
            req.image_base64
        )

        return {"answer": answer}

    context = build_context(req)

    messages = [
        {"role": "system", "content": "You are a precise data analyst."},
        {"role": "user", "content": context},
    ]

    async def event_stream():

        async for token in ollama_stream(messages):

            yield f"data: {json.dumps({'token': token})}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )