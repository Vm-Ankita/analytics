import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL     = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL        = os.getenv("OLLAMA_MODEL","llama3")
OLLAMA_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llava")
MAX_TEXT_CHARS      = int(os.getenv("MAX_TEXT_CHARS", "5000"))
MAX_TOKENS          = int(os.getenv("MAX_TOKENS", "400"))
