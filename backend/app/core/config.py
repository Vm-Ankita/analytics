'''import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL     = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL        = os.getenv("OLLAMA_MODEL","llama3")
OLLAMA_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llava")
MAX_TEXT_CHARS      = int(os.getenv("MAX_TEXT_CHARS", "5000"))
MAX_TOKENS          = int(os.getenv("MAX_TOKENS", "400"))
'''







import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ==============================
# Ollama Configuration
# ==============================

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llava")

# ==============================
# Token & Input Limits
# ==============================

MAX_TEXT_CHARS = int(os.getenv("MAX_TEXT_CHARS", "5000"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "400"))

# ==============================
# Generation Parameters
# ==============================

TEMPERATURE = float(os.getenv("TEMPERATURE", "0.0"))
CONTEXT_WINDOW = int(os.getenv("CONTEXT_WINDOW", "1024"))

# ==============================
# HTTP Timeouts
# ==============================

CONNECT_TIMEOUT = float(os.getenv("CONNECT_TIMEOUT", "8"))
READ_TIMEOUT = float(os.getenv("READ_TIMEOUT", "900"))
WRITE_TIMEOUT = float(os.getenv("WRITE_TIMEOUT", "2000"))
POOL_TIMEOUT = float(os.getenv("POOL_TIMEOUT", "5"))