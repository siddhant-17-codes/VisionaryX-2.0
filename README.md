# VisionaryX 2.0

> **Intelligence, not just answers.**

A full-stack AI workspace that cites its sources. Query documents with page-level citations, analyse images with Gemini Vision, generate visuals with FLUX — all with persistent chat history across sessions.

**Live demo:** *[Add your Vercel URL after deployment]*  
**Backend:** FastAPI + Python · **Frontend:** React + Vite + Tailwind CSS

---

## Why VisionaryX?

Most AI chat tools give you answers. VisionaryX gives you **answers with evidence** — every response from a PDF query traces back to a specific page in your document. Built on a production-grade RAG pipeline at a time when document querying required real engineering effort, now rebuilt as a modern full-stack product.

---

## Features

| Feature | Description | Stack |
|---|---|---|
| **PDF Chat + RAG** | Upload PDF or DOCX, ask questions, get cited answers with page numbers | FAISS · LangChain · Gemini |
| **General Chat** | Persistent conversation memory, session history, streaming responses | Gemini 2.5 Flash |
| **Image Query** | Upload any image, ask anything, Gemini Vision responds in detail | Gemini Vision |
| **Text to Image** | Describe your visual, generate and download | FLUX.1-schnell · HuggingFace |
| **Session History** | All chats saved to disk, browsable sidebar like ChatGPT | Local JSON storage |
| **Streaming** | Word-by-word response rendering for natural LLM feel | React state streaming |

---

## Architecture

```
VisionaryX-2.0/
├── backend/                    # FastAPI — Python 3.11
│   ├── main.py                 # App entry, middleware, exception handlers
│   ├── routers/                # chat · pdf · image · generate · sessions
│   ├── services/               # gemini_service · rag_service · image_service
│   ├── core/                   # chunker · embeddings · vector_store · storage · exceptions
│   ├── models/schemas.py       # Pydantic request/response models
│   ├── config/                 # settings (pydantic-settings) · logger
│   └── storage/                # chats/*.json · documents/*/ (runtime, gitignored)
│
└── frontend/                   # React 18 + Vite + Tailwind CSS
    └── src/
        ├── pages/              # Landing · Chat · PDFChat · ImageQuery · TextToImage · NotFound
        ├── components/         # layout/ · chat/ · pdf/ · image/ · icons/
        ├── hooks/              # useChat · usePDF · useImage · useSessions
        ├── api/                # axios client + typed API functions
        ├── context/            # SessionContext (global session state)
        └── utils/              # errorHandler (centralized error parsing)
```

### RAG Pipeline

```
Upload PDF/DOCX
     ↓
Extract text per page (pypdf / python-docx)
     ↓
Semantic chunking (RecursiveCharacterTextSplitter, 1000 chars, 150 overlap)
     ↓
Embed chunks (Google gemini-embedding-001)
     ↓
Store in FAISS index (per session UUID)
     ↓
Query → embed question → similarity search → adaptive threshold filtering
     ↓
Top-k chunks → Gemini 2.5 Flash → answer + page citations
```

---

## Tech Stack

**Backend**
- Python 3.11, FastAPI, Uvicorn
- LangChain 0.3, LangChain-Google-GenAI
- FAISS-CPU for vector search
- Google Gemini 2.5 Flash (chat, vision, embeddings)
- HuggingFace Inference (FLUX.1-schnell image generation)
- PyPDF, python-docx for document parsing
- Pydantic v2, pydantic-settings

**Frontend**
- React 18, Vite 5, React Router v6
- Tailwind CSS 3 (custom dark design system)
- Axios, react-hot-toast, react-markdown
- Custom SVG icon set (Feather-style)

**Deployment**
- Frontend: Vercel
- Backend: Render (free tier)

---

## Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### 1. Clone the repository

```bash
git clone https://github.com/siddhant-17-codes/VisionaryX-2.0.git
cd VisionaryX-2.0
```

### 2. Backend setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
GOOGLE_API_KEY=your_google_gemini_api_key
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token
ALLOWED_ORIGINS=http://localhost:5173,https://your-vercel-app.vercel.app
```

### 4. Frontend setup

```bash
cd ../frontend
npm install
```

---

## Running the Application

### Run both together (recommended)

```bash
# From project root
make dev
```

### Run individually

```bash
# Terminal 1 — Backend
make run-backend
# → http://127.0.0.1:8000
# → http://127.0.0.1:8000/docs (Swagger UI)

# Terminal 2 — Frontend
make run-frontend
# → http://localhost:5173
```

---

## API Key Setup

### Google Gemini API Key
1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Click **Create API key** → **Create new project**
3. Copy the key (starts with `AIza...`)
4. Paste into `.env` as `GOOGLE_API_KEY`

### HuggingFace Token
1. Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Click **New token** → Read access is sufficient
3. Copy and paste into `.env` as `HUGGINGFACEHUB_API_TOKEN`

---

## API Quota Considerations

VisionaryX uses the **Gemini free tier** which has the following limits:

| Metric | Free Tier Limit |
|---|---|
| Requests per minute | 15 RPM |
| Requests per day | 1,500 RPD |
| Input tokens per minute | Varies by model |

**Tips to avoid hitting quota:**
- Space out requests — avoid rapid consecutive queries
- The app detects quota errors and shows a clear fallback UI with retry guidance
- Quota resets every 24 hours
- For production deployment, upgrade to a paid Gemini API plan

HuggingFace free inference for FLUX.1-schnell: no daily limit, but response time may vary (5–30s depending on model warm-up state).

---

## Usage Guide

### PDF Chat
1. Click **PDF Chat** in the sidebar
2. Upload one or more PDF or DOCX files
3. Wait for indexing (3–10 seconds) — suggested questions appear automatically
4. Ask anything — every answer shows page-level source citations
5. Click a file name in the header to open the original document

### General Chat
1. Click **Chat** in the sidebar
2. Type any question and press Enter (Shift+Enter for new line)
3. Conversation memory is maintained across turns
4. Click **Recent** sessions in the sidebar to restore previous conversations

### Image Query
1. Click **Image Query** in the sidebar
2. Upload any JPG or PNG image
3. Optionally type a specific question
4. Click **Analyse Image** — Gemini Vision responds in detail

### Text to Image
1. Click **Text to Image** in the sidebar
2. Describe what you want to see in detail
3. Click **Generate Image** (takes 15–30 seconds)
4. Download the result when ready

---

## Configuration

| Variable | Description | Required |
|---|---|---|
| `GOOGLE_API_KEY` | Google Gemini API key | Yes |
| `HUGGINGFACEHUB_API_TOKEN` | HuggingFace inference token | Yes |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins | Yes |

Frontend environment (optional, create `frontend/.env`):

```env
VITE_API_URL=http://localhost:8000
```

---

## Project Structure — Key Files

| File | Purpose |
|---|---|
| `backend/main.py` | FastAPI app, CORS, middleware, exception handlers |
| `backend/core/chunker.py` | PDF/DOCX extraction + semantic chunking |
| `backend/core/vector_store.py` | FAISS index build/load per session |
| `backend/services/rag_service.py` | RAG pipeline with adaptive threshold |
| `backend/services/gemini_service.py` | All Gemini API calls (chat, vision, embed) |
| `backend/core/storage.py` | JSON-based chat session persistence |
| `frontend/src/hooks/useChat.js` | Chat state, streaming, session restore |
| `frontend/src/hooks/usePDF.js` | PDF upload, RAG query, citation state |
| `frontend/src/utils/errorHandler.js` | Centralized API error parsing |
| `frontend/src/context/SessionContext.jsx` | Global session list state |

---

## Scaling & Production Notes

For production deployment beyond portfolio use:

- **Rate limiting:** Add `slowapi` to FastAPI routes (10–20 RPM per IP)
- **Async services:** Convert Gemini/HuggingFace calls to `async def` for concurrency
- **Background processing:** Move PDF indexing to FastAPI `BackgroundTasks` so upload returns instantly
- **Authentication:** JWT-based auth with `python-jose` + `passlib`
- **Database:** Replace JSON file storage with PostgreSQL + SQLAlchemy for session management
- **Secret management:** Move from `.env` to AWS Secrets Manager or HashiCorp Vault
- **CI/CD:** GitHub Actions → auto-deploy to Render on merge to `main`
- **Monitoring:** Sentry for error tracking, Vercel Analytics for frontend

---

## Contributing

Contributions are welcome. Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit with clear messages (`git commit -m 'feat: add X'`)
4. Push and open a Pull Request

Please keep PRs focused — one feature or fix per PR.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Author

**Siddhant Thakur**  
MCA · Techno Main Salt Lake (MAKAUT) · Kolkata, India  
[GitHub](https://github.com/siddhant-17-codes) · [LinkedIn](https://linkedin.com/in/siddhant-thakur)

---

*VisionaryX started as a Minor Project in 2024 — a RAG pipeline built when LLM APIs were not freely accessible. Version 2.0 rebuilds it as a production-grade full-stack application with a proper separation of concerns, citation-aware responses, persistent sessions, and a modern React frontend.*
