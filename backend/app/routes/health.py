"""
Health check endpoint.

Verifies if Ollama server is reachable.
"""

from fastapi import APIRouter
import httpx

from app.core.config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_VISION_MODEL

router = APIRouter()


@router.get("/health")
async def health():

    try:

        async with httpx.AsyncClient(timeout=5) as client:

            r = await client.get(f"{OLLAMA_BASE_URL}/api/tags")

            if r.status_code == 200:

                models = [m["name"] for m in r.json().get("models", [])]

                return {
                    "status": "ok",
                    "ollama": "connected",
                    "model": OLLAMA_MODEL,
                    "vision_model": OLLAMA_VISION_MODEL,
                    "available_models": models,
                }

    except Exception:
        pass

    return {
        "status": "ok",
        "ollama": "disconnected",
        "model": OLLAMA_MODEL,
        "vision_model": OLLAMA_VISION_MODEL,
        "available_models": [],
    }