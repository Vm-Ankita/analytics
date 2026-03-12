from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import httpx

from app.routes import analyze, ask, models, health
from app.core.config import OLLAMA_BASE_URL, OLLAMA_MODEL

app = FastAPI(title="Datalyze AI", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(analyze.router)
app.include_router(ask.router)
app.include_router(models.router)


@app.on_event("startup")
async def warmup():
    """Pre-load model into GPU/RAM so the first request is instant."""
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model":   OLLAMA_MODEL,
                    "prompt":  "hi",
                    "stream":  False,
                    "options": {"num_predict": 1},
                },
            )
        print(f"✅ Model '{OLLAMA_MODEL}' warmed up")
    except Exception as e:
        print(f"⚠  Warmup skipped (start Ollama first): {e}")


# Serve built React frontend in production
DIST = Path(__file__).parent.parent.parent / "frontend" / "dist"
if DIST.exists():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def spa(full_path: str):
        return FileResponse(DIST / "index.html")
