"""
Ollama Client

Handles communication with the local Ollama server.
Supports:
- streaming chat
- vision analysis
"""

import httpx
import json
from typing import AsyncGenerator, List, Dict

from fastapi import HTTPException

from app.core.config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_VISION_MODEL,
    MAX_TOKENS,
    MAX_TEXT_CHARS,
    TEMPERATURE,
    CONTEXT_WINDOW,
    CONNECT_TIMEOUT,
    READ_TIMEOUT,
    WRITE_TIMEOUT,
    POOL_TIMEOUT,
)


# -----------------------------------------------------
# Generation parameters
# -----------------------------------------------------

OPTIONS = {
    "num_predict": MAX_TOKENS,
    "temperature": TEMPERATURE,
    "num_ctx": CONTEXT_WINDOW,
}


# -----------------------------------------------------
# HTTP client configuration
# -----------------------------------------------------

TIMEOUT = httpx.Timeout(
    connect=CONNECT_TIMEOUT,
    read=READ_TIMEOUT,
    write=WRITE_TIMEOUT,
    pool=POOL_TIMEOUT,
)

client = httpx.AsyncClient(timeout=TIMEOUT)


# -----------------------------------------------------
# Clean messages
# -----------------------------------------------------

def clean_messages(messages: List[Dict]) -> List[Dict]:

    cleaned = []

    for m in messages:

        role = str(m.get("role", "")).strip()
        content = str(m.get("content", "")).strip()

        if not role or not content:
            continue

        if len(content) > MAX_TEXT_CHARS:
            content = content[:MAX_TEXT_CHARS] + "\n[truncated]"

        cleaned.append({
            "role": role,
            "content": content,
        })

    return cleaned


# -----------------------------------------------------
# Check Ollama server
# -----------------------------------------------------

async def check_ollama_running() -> bool:

    try:
        r = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
        return r.status_code == 200
    except Exception:
        return False


# -----------------------------------------------------
# Streaming chat
# -----------------------------------------------------

async def ollama_stream(
    messages: List[Dict],
    model: str | None = None
) -> AsyncGenerator[str, None]:

    clean = clean_messages(messages)

    if not clean:
        yield "No input provided."
        return

    if not await check_ollama_running():
        yield "❌ Ollama not running. Run: ollama serve"
        return

    payload = {
        "model": model or OLLAMA_MODEL,
        "messages": clean,
        "stream": True,
        "options": OPTIONS,
    }

    try:

        async with client.stream(
            "POST",
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
        ) as r:

            async for line in r.aiter_lines():

                if not line:
                    continue

                try:
                    data = json.loads(line)

                    token = data.get("message", {}).get("content", "")

                    if token:
                        yield token

                    if data.get("done"):
                        break

                except json.JSONDecodeError:
                    continue

    except httpx.ReadTimeout:
        yield "\n⚠ Ollama response timed out."


# -----------------------------------------------------
# Vision model
# -----------------------------------------------------

async def ollama_vision(prompt: str, image_b64: str) -> str:

    payload = {
        "model": OLLAMA_VISION_MODEL,
        "prompt": prompt[:MAX_TEXT_CHARS],
        "images": [image_b64],
        "stream": False,
        "options": {
            "num_predict": MAX_TOKENS,
            "temperature": TEMPERATURE,
        },
    }

    try:

        r = await client.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
        )

        r.raise_for_status()

        return r.json().get("response", "")

    except httpx.ConnectError:
        raise HTTPException(503, "Ollama not reachable")

    except httpx.ReadTimeout:
        raise HTTPException(504, "Vision model timed out")

    except httpx.HTTPStatusError as e:
        raise HTTPException(502, f"Ollama error: {e.response.text[:200]}")