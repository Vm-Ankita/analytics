# Datalyze AI — Local AI Analytics

Upload any file. Get instant stats, auto-charts, and streaming AI insights.
100% local — no API keys, no internet required.

---

## Features

- **Instant stats** — pandas computes rows, cols, min/max/avg/std/outliers before LLM runs
- **Auto charts** — matplotlib generates bar/line charts automatically
- **Auto-detected patterns** — IQR outliers, trends, correlations detected without LLM
- **Streaming insights** — LLM tokens appear as they generate (no waiting)
- **Streaming Q&A** — chat with your file, responses stream live
- **30+ file types** — CSV, Excel, PDF, Word, JSON, images, code, logs
- **Model warmup** — model pre-loaded on startup so first request is instant

---

## Quick Start

### 1. Install Ollama + pull a model

```bash
# Install Ollama: https://ollama.com
ollama pull llama3.2:1b    # fast 1B model (recommended)
ollama serve               # start Ollama server
```

### 2. Backend

```bash
cd backend
python3.10 -m venv venv

# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000**

---

## Project Structure

```
datalyze-v3/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI app + model warmup
│   │   ├── core/
│   │   │   └── config.py               # env config
│   │   ├── schemas/
│   │   │   └── chat.py                 # Pydantic models
│   │   ├── utils/
│   │   │   └── file_types.py           # file type registry
│   │   ├── parsers/
│   │   │   ├── csv_parser.py
│   │   │   ├── excel_parser.py
│   │   │   ├── json_parser.py
│   │   │   ├── pdf_parser.py
│   │   │   └── docx_parser.py
│   │   ├── services/
│   │   │   ├── ollama_client.py        # streaming LLM client
│   │   │   ├── analytics_engine.py     # pandas stats + auto insights
│   │   │   ├── chart_generator.py      # matplotlib auto-charts
│   │   │   └── prompts.py              # system prompts + builders
│   │   └── routes/
│   │       ├── analyze.py              # POST /api/analyze (SSE stream)
│   │       ├── ask.py                  # POST /api/ask (SSE stream)
│   │       ├── models.py               # GET /api/models
│   │       └── health.py               # GET /health
│   ├── requirements.txt
│   └── .env
└── frontend/
    ├── index.html
    ├── vite.config.js
    ├── package.json
    └── src/
        ├── main.jsx
        ├── index.css
        ├── api.js                      # fetch + SSE stream helpers
        ├── markdown.js                 # lightweight markdown renderer
        ├── App.jsx                     # root state + handlers
        └── components/
            ├── Topbar.jsx
            ├── UploadView.jsx
            ├── AnalyzingView.jsx
            ├── Workspace.jsx
            ├── AnalysisPanel.jsx       # chart + auto-insights + LLM insights
            └── ChatPanel.jsx           # streaming chat UI
```

---

## Configuration

Edit `backend/.env`:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b        # change model here
OLLAMA_VISION_MODEL=llava        # for image analysis
MAX_TOKENS=400                   # response length
MAX_TEXT_CHARS=5000              # input truncation
```

### Faster models
| Model | Speed | Quality |
|-------|-------|---------|
| `llama3.2:1b` | ⚡⚡⚡ Fastest | Good |
| `phi3:mini` | ⚡⚡⚡ Very fast | Good |
| `llama3.2` | ⚡⚡ Fast | Better |
| `llama3.1:8b` | ⚡ Slower | Best |

---

## How it works

1. File uploaded → parsed by file-type-specific parser
2. Tabular data → pandas computes full stats + auto-detects outliers/trends/correlations
3. Pandas generates matplotlib chart (base64 PNG)
4. Metadata + chart sent to frontend **immediately** via SSE
5. Frontend switches to workspace view — user sees stats + chart before LLM starts
6. LLM streams insight tokens → frontend renders them live
7. User asks questions → responses stream token-by-token

---

## Production build

```bash
cd frontend && npm run build
# Then just run the backend — it serves the built frontend
cd ../backend
uvicorn app.main:app --port 8000
```

Open **http://localhost:8000**
