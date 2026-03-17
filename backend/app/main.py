"""
Application entry point.

Creates FastAPI server, registers routes,
warms up the LLM model, and serves the React frontend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from pathlib import Path
import httpx

from app.routes import analyze, ask, models, health
from app.core.config import OLLAMA_BASE_URL, OLLAMA_MODEL


# -----------------------------------------------------
# FastAPI application
# -----------------------------------------------------

app = FastAPI(
    title="Datalyze AI",
    version="3.0.0",
)


# -----------------------------------------------------
# CORS configuration
# -----------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------
# Register API routes
# -----------------------------------------------------

app.include_router(health.router)
app.include_router(analyze.router)
app.include_router(ask.router)
app.include_router(models.router)


# -----------------------------------------------------
# Model warmup (runs on server startup)
# -----------------------------------------------------

@app.on_event("startup")
async def warmup_model():
    """
    Preload the Ollama model so first request is fast.
    """

    try:

        async with httpx.AsyncClient(timeout=60) as client:

            await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": "hi",
                    "stream": False,
                    "options": {"num_predict": 1},
                },
            )

        print(f"✅ Model '{OLLAMA_MODEL}' warmed up")

    except Exception as e:

        print(f"⚠ Warmup skipped (start Ollama first): {e}")


# -----------------------------------------------------
# Serve React frontend (production build)
# -----------------------------------------------------

DIST = Path(__file__).parent.parent.parent / "frontend" / "dist"

if DIST.exists():

    # Static assets
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    # React SPA fallback
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        return FileResponse(DIST / "index.html")