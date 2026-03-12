from fastapi import APIRouter, HTTPException
import httpx
from app.core.config import OLLAMA_BASE_URL, OLLAMA_MODEL

router = APIRouter(prefix="/api")


@router.get("/models")
async def list_models():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            r.raise_for_status()
            models = [
                {
                    "name": m["name"],
                    "size": f"{m.get('size', 0) / 1e9:.1f} GB" if m.get("size") else "?",
                }
                for m in r.json().get("models", [])
            ]
            return {"models": models, "current_model": OLLAMA_MODEL}
    except Exception as e:
        raise HTTPException(503, f"Cannot reach Ollama: {e}")
