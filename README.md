# VisionaryX 2.0

A full-stack AI workspace built with **FastAPI** + **React** + **FAISS**.  
Query documents with citations, analyse images, and generate visuals — all in one interface.

**Live demo:** _[Add Vercel URL after deployment]_

---

## Features

| Feature | Description |
|---|---|
| General Chat | Conversational AI with full memory across turns |
| PDF Chat + RAG | Upload multiple PDFs, get answers with page-level citations |
| Suggested Questions | AI auto-generates 3 questions after PDF upload |
| Image Query | Analyse any image using Gemini Vision |
| Text to Image | Generate visuals from text prompts via HuggingFace |

## Architecture

```
VisionaryX-2.0/
├── backend/               # FastAPI
│   ├── routers/           # chat · pdf · image · generate
│   ├── services/          # gemini_service · rag_service · image_service
│   ├── core/              # chunker · embeddings · vector_store (FAISS)
│   ├── models/schemas.py  # Pydantic request/response models
│   └── main.py
└── frontend/              # React + Vite + Tailwind
    └── src/
        ├── pages/         # Home · Chat · PDFChat · ImageQuery · TextToImage
        ├── components/    # ChatWindow · CitationCard · SuggestedQuestions …
        ├── api/           # axios client + typed API calls
        └── hooks/         # useChat · usePDF · useImage
```

## Tech Stack

**Backend:** Python 3.11 · FastAPI · LangChain · Google Gemini 1.5 Flash · FAISS · PyPDF  
**Frontend:** React 18 · Vite · Tailwind CSS · React Router · Axios  
**Deployment:** Vercel (frontend) · Render (backend)

## Local Setup

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # fill in your API keys
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`

## Environment Variables

```env
GOOGLE_API_KEY=your_google_gemini_api_key
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token
ALLOWED_ORIGINS=http://localhost:5173,https://your-vercel-app.vercel.app
```

## Origin

VisionaryX started as a Minor Project in 2024 — a RAG pipeline for document querying using FAISS and LangChain, built at a time when LLM APIs were not freely accessible. Version 2.0 rebuilds it as a production-grade full-stack application with a proper separation of concerns, citation-aware responses, and a modern React frontend.

---

Built by [Siddhant Thakur](https://github.com/siddhant-17-codes)
