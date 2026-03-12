'''import httpx
import json
from typing import AsyncGenerator
from fastapi import HTTPException
from app.core.config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_VISION_MODEL, MAX_TOKENS

# temperature=0.1 → precise answers, not creative
# num_ctx=4096    → sees more data per request
# num_predict     → enough tokens to finish answers
_OPTIONS = {"num_predict": MAX_TOKENS, "temperature": 0.1, "num_ctx": 4096}


async def ollama_stream(messages: list, model: str = None) -> AsyncGenerator[str, None]:
    """Streaming chat — tokens yielded as soon as generated."""
    payload = {
        "model":    model or OLLAMA_MODEL,
        "messages": messages,
        "stream":   True,
        "options":  _OPTIONS,
    }
    async with httpx.AsyncClient(timeout=180.0) as client:
        try:
            async with client.stream("POST", f"{OLLAMA_BASE_URL}/api/chat", json=payload) as r:
                r.raise_for_status()
                async for line in r.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        chunk = json.loads(line)
                        token = chunk.get("message", {}).get("content", "")
                        if token:
                            yield token
                        if chunk.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue
        except httpx.ConnectError:
            yield "\n\n⚠ Ollama not reachable. Run: ollama serve"


async def ollama_vision(prompt: str, image_b64: str) -> str:
    """Vision model generate (non-streaming)."""
    payload = {
        "model":   OLLAMA_VISION_MODEL,
        "prompt":  prompt,
        "images":  [image_b64],
        "stream":  False,
        "options": {"num_predict": MAX_TOKENS, "temperature": 0.1},
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            r = await client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
            r.raise_for_status()
            return r.json().get("response", "")
        except httpx.ConnectError:
            raise HTTPException(503, "Ollama not reachable. Run: ollama serve")
        except httpx.HTTPStatusError as e:
            raise HTTPException(502, f"Ollama vision error: {e.response.text}")'''










import httpx
import json
from typing import AsyncGenerator
from fastapi import HTTPException
from app.core.config import OLLAMA_BASE_URL, OLLAMA_MODEL, MAX_TOKENS

_OPTIONS = {
    "num_predict": MAX_TOKENS,
    "temperature": 0.0,
    "num_ctx":     1024,
}

_TIMEOUT = httpx.Timeout(connect=8.0, read=900.0, write=2000.0, pool=5.0)


async def ollama_stream(messages: list, model: str = None) -> AsyncGenerator[str, None]:

    # sanitize messages
    clean = [
        {"role": str(m.get("role","")).strip(), "content": str(m.get("content","")).strip()}
        for m in messages
        if str(m.get("role","")).strip() and str(m.get("content","")).strip()
    ]
    if not clean:
        yield "No input provided."
        return

    # truncate huge messages
    for i, m in enumerate(clean):
        if len(m["content"]) > 2000:
            clean[i]["content"] = m["content"][:2000] + "\n[truncated]"

    payload = {
        "model":    model or OLLAMA_MODEL,
        "messages": clean,
        "stream":   True,
        "options":  _OPTIONS,
    }

    # pre-flight check
    try:
        async with httpx.AsyncClient(timeout=5.0) as probe:
            r = await probe.get(f"{OLLAMA_BASE_URL}/api/tags")
            if r.status_code != 200:
                yield "❌ Ollama is running but returned an error. Try restarting it."
                return
    except httpx.ConnectError:
        yield "❌ Ollama is not running. Open a terminal and run: ollama serve"
        return
    except Exception:
        yield "❌ Cannot reach Ollama at localhost:11434."
        return

    # stream tokens
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            async with client.stream(
                "POST", f"{OLLAMA_BASE_URL}/api/chat", json=payload
            ) as r:
                if r.status_code == 404:
                    yield f"❌ Model '{payload['model']}' not found. Run: ollama pull {payload['model']}"
                    return
                if r.status_code != 200:
                    body = await r.aread()
                    yield f"❌ Ollama error {r.status_code}: {body.decode()[:200]}"
                    return

                buf = b""
                token_count = 0
                async for chunk in r.aiter_bytes(chunk_size=64):
                    if not chunk:
                        continue
                    buf += chunk
                    while b"\n" in buf:
                        line, buf = buf.split(b"\n", 1)
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            data  = json.loads(line)
                            token = data.get("message", {}).get("content", "")
                            if token:
                                token_count += 1
                                yield token
                            if data.get("done"):
                                if token_count == 0:
                                    yield "⚠ Model returned an empty response. Try rephrasing."
                                return
                        except json.JSONDecodeError:
                            continue

    except httpx.ReadTimeout:
        yield "\n\n⚠ Timed out. Switch to faster model: set OLLAMA_MODEL=llama3.2:1b in .env"
    except httpx.ConnectError:
        yield "❌ Lost connection to Ollama. Run: ollama serve"
    except Exception as e:
        yield f"❌ {type(e).__name__}: {e}"


async def ollama_vision(prompt: str, image_b64: str) -> str:
    payload = {
        "model":   "llava",
        "prompt":  prompt[:2000],
        "images":  [image_b64],
        "stream":  False,
        "options": {"num_predict": 500, "temperature": 0.1},
    }
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
            r.raise_for_status()
            return r.json().get("response", "")
    except httpx.ConnectError:
        raise HTTPException(503, "Ollama not reachable.")
    except httpx.ReadTimeout:
        raise HTTPException(504, "Vision model timed out.")
    except httpx.HTTPStatusError as e:
        raise HTTPException(502, f"Ollama error: {e.response.text[:200]}")