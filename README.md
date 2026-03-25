# PDF Intelligence API

An intelligent PDF document processing system that extracts insights, enables semantic search, and answers questions about your documents using LLMs and vector search.

---

## What It Does

Upload a PDF and get:

- **Instant chat** — Ask questions about the document within seconds (RAG-powered)
- **AI-extracted insights** — Document type, categories, summaries, key topics, named entities
- **Semantic search** — Find relevant chunks using vector embeddings
- **Structured analysis** — People, organizations, locations, dates, monetary values extracted automatically

---

## Architecture Overview

```
┌────────────────────────────────────────────────────────────┐
│                        FastAPI Backend                      │
│                                                            │
│  POST /upload ──► DocumentProcessor (BackgroundTask)       │
│                        │                                   │
│               ┌────────▼────────┐                         │
│               │  PHASE 1 (~30s) │                         │
│               │  Parse PDF      │  Docling                 │
│               │  Clean Markdown │                         │
│               │  Chunk by Header│  LangChain               │
│               │  ┌─────────┐   │                         │
│               │  │Embed +  │   │  OpenAI / Gemini         │
│               │  │Store    │   │  Qdrant Vector DB         │
│               │  │Vectors  │   │                         │
│               │  └─────────┘   │                         │
│               │  Save Chunks   │  SQLite / PostgreSQL      │
│               │  to DB         │                         │
│               └────────────────┘                         │
│                  Status: CHAT_READY ✓                      │
│                        │                                   │
│               ┌────────▼────────┐                         │
│               │  PHASE 2 (~60s) │                         │
│               │  LLM Analysis   │  Map-Reduce for          │
│               │  (type, summary,│  large docs              │
│               │   entities,     │                         │
│               │   insights)     │                         │
│               └────────────────┘                         │
│                  Status: COMPLETED ✓                       │
│                                                            │
│  POST /ask ──► RAGService                                  │
│               ├─ Vector Search (Qdrant)                    │
│               ├─ Keyword Search (SQL ILIKE)                │
│               ├─ Merge & Deduplicate                       │
│               └─ LLM Answer Generation                     │
└────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web Framework | FastAPI 0.115 + Uvicorn |
| PDF Parsing | IBM Docling |
| LLM | OpenAI (gpt-4o-mini) or Google Gemini |
| Embeddings | OpenAI / Gemini Embedding |
| Vector DB | Qdrant |
| Relational DB | SQLite (dev) / PostgreSQL (prod) |
| ORM | SQLAlchemy 2.0 |
| Chunking | LangChain MarkdownHeaderTextSplitter |
| Validation | Pydantic v2 |

---

## Project Structure

```
pdf-intelligence/
├── backend/
│   ├── app/
│   │   ├── main.py                      # FastAPI app + lifespan
│   │   ├── api/v1/
│   │   │   ├── routes/                  # HTTP route definitions
│   │   │   │   ├── document_routes.py
│   │   │   │   ├── session_routes.py
│   │   │   │   └── health_routes.py
│   │   │   ├── controllers/             # Request/response handling
│   │   │   ├── services/                # Business logic
│   │   │   ├── repository/              # Database access layer
│   │   │   ├── models/
│   │   │   │   ├── entities/            # SQLAlchemy ORM models
│   │   │   │   ├── request/             # Pydantic request schemas
│   │   │   │   ├── response/            # Pydantic response schemas
│   │   │   │   └── enums/               # DocumentStatus enum
│   │   │   └── dependencies/            # DI container + FastAPI deps
│   │   ├── core/
│   │   │   ├── config.py                # Pydantic settings
│   │   │   ├── database.py              # DB engine + session + init
│   │   │   ├── exceptions.py            # Custom exception classes
│   │   │   └── response_wrapper.py      # Standardized API response
│   │   ├── extraction/
│   │   │   ├── pipeline/
│   │   │   │   └── document_pipeline.py # Orchestrates Phase 1 + 2
│   │   │   ├── preprocessing/
│   │   │   │   ├── docling_parser.py    # PDF → Markdown
│   │   │   │   ├── markdown_cleaner.py  # Noise removal
│   │   │   │   └── chunking.py          # Header-based chunking
│   │   │   ├── analysis/
│   │   │   │   ├── document_analyzer.py # Direct / Map-Reduce LLM
│   │   │   │   ├── schemas.py           # DocumentIntelligence schema
│   │   │   │   └── prompts/             # LLM prompt templates
│   │   │   ├── embeddings/
│   │   │   │   └── embedding_service.py # Parallel batch embedding
│   │   │   ├── llm/                     # LLM factory + providers
│   │   │   ├── llm_embedding/           # Embedding factory + providers
│   │   │   ├── vector_store/
│   │   │   │   └── qdrant_service.py    # Qdrant upsert + search
│   │   │   └── rag/
│   │   │       └── rag_service.py       # Hybrid retrieval + answer
│   │   ├── middleware/                  # Exception handler, logging
│   │   ├── processors/
│   │   │   └── document_processor.py   # Background task runner
│   │   └── utils/
│   │       └── file_handler.py         # Validate + save uploads
│   ├── alembic/                         # DB migrations
│   ├── requirements.txt
│   └── .env.example
├── qdrant_data/                         # Local Qdrant storage
└── uploaded_files/                      # Temporary PDF storage
```

---

## Document Processing Pipeline

### Phase 1 — Parse & Index (runs in background, ~5–30s)

1. **Parse** — Docling converts the PDF to structured Markdown preserving headers, tables, and lists
2. **Clean** — Remove artifacts, excessive whitespace, and formatting noise
3. **Chunk** — Split Markdown by header hierarchy (H1/H2/H3) into semantic chunks
4. **Embed + Store** *(parallel threads)*
   - Thread A: Embed all chunks via OpenAI/Gemini, upsert into Qdrant
   - Thread B: Save chunk text to PostgreSQL (with TSVECTOR for keyword search)

**Status → `CHAT_READY`** — User can start asking questions

### Phase 2 — Analyze (runs after Phase 1, ~30–120s)

Uses LLM to extract structured intelligence. Automatically adapts strategy:

- **Small docs** (≤ 12,000 chars): single LLM call
- **Large docs** (> 12,000 chars): Map-Reduce — parallel chunk summaries → final synthesis

Extracts:
- Document type, category, sub-category
- Short summary + detailed summary
- Key topics
- Named entities: people, organizations, locations, dates, monetary values
- 3–8 key insights
- Document sections with summaries

**Status → `COMPLETED`**

### RAG Question Answering

```
User Question
     │
     ├─► Embed question
     ├─► Vector search in Qdrant (top-5 semantic chunks)
     ├─► Keyword search in PostgreSQL (ILIKE)
     ├─► Merge + deduplicate results
     └─► LLM generates grounded answer with sources
```

---

## Document Status Flow

```
UPLOADED → PROCESSING → CHAT_READY → ANALYZING → COMPLETED
                                             ↘
                                           FAILED
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/api/v1/session` | Get or create anonymous session |
| `POST` | `/api/v1/documents/upload` | Upload a PDF |
| `GET` | `/api/v1/documents` | List your documents |
| `GET` | `/api/v1/documents/{id}` | Get document details + analysis |
| `GET` | `/api/v1/documents/{id}/insights` | Get extracted insights |
| `GET` | `/api/v1/documents/{id}/chunks` | Get document chunks |
| `POST` | `/api/v1/documents/{id}/ask` | Ask a question (RAG) |

All endpoints accept an `X-Anon-ID` header to associate requests with an anonymous user session. If omitted, a new session is created automatically.

---

## Setup & Installation

### Prerequisites

- Python 3.12+
- OpenAI API key or Google Gemini API key

### 1. Clone & Install

```bash
git clone <repo-url>
cd pdf-intelligence

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r backend/requirements.txt
```

### 2. Configure Environment

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

```env
APP_NAME=PDF Intelligence API
APP_ENV=development

# Database
DATABASE_URL=sqlite:///./pdf_intelligence.db

# LLM — choose one provider
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-...

# Embedding
EMBEDDING_MODEL=text-embedding-3-small

# Vector DB (leave blank to use local ./qdrant_data)
QDRANT_URL=
QDRANT_API_KEY=

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**To use Google Gemini instead of OpenAI:**

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-1.5-flash
GEMINI_API_KEY=AIza...
EMBEDDING_MODEL=models/gemini-embedding-001
QDRANT_VECTOR_SIZE=768
```

### 3. Start Qdrant (optional, recommended)

```bash
docker run -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_data:/qdrant/storage \
  qdrant/qdrant:latest
```

Then set in `.env`:
```env
QDRANT_URL=http://localhost:6333
```

Without Docker, Qdrant runs in local file mode (`./qdrant_data`) automatically.

### 4. Run the Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

The database is created automatically on first startup.

---

## Example Usage

```bash
# 1. Upload a PDF
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "X-Anon-ID: my-user-id" \
  -F "file=@report.pdf"

# Response:
# { "data": { "document_id": "abc-123", "status": "PROCESSING" } }

# 2. Poll until CHAT_READY (usually < 30 seconds)
curl http://localhost:8000/api/v1/documents/abc-123 \
  -H "X-Anon-ID: my-user-id"

# 3. Ask a question
curl -X POST http://localhost:8000/api/v1/documents/abc-123/ask \
  -H "X-Anon-ID: my-user-id" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the key findings?"}'

# Response:
# { "data": { "answer": "...", "sources": ["chunk text 1", "chunk text 2"] } }

# 4. Get AI-extracted insights (available after COMPLETED)
curl http://localhost:8000/api/v1/documents/abc-123/insights \
  -H "X-Anon-ID: my-user-id"
```

---

## Configuration Reference

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | `development` or `production` |
| `DATABASE_URL` | `sqlite:///./pdf_intelligence.db` | SQLAlchemy DB URL |
| `LLM_PROVIDER` | `openai` | `openai` or `gemini` |
| `LLM_MODEL` | `gpt-4o-mini` | Model name for the selected provider |
| `LLM_TEMPERATURE` | `0.0` | LLM temperature (0 = deterministic) |
| `OPENAI_API_KEY` | — | Required if `LLM_PROVIDER=openai` |
| `GEMINI_API_KEY` | — | Required if `LLM_PROVIDER=gemini` |
| `EMBEDDING_MODEL` | `models/gemini-embedding-001` | Embedding model |
| `QDRANT_URL` | `None` | Remote Qdrant URL (optional) |
| `QDRANT_PATH` | `./qdrant_data` | Local Qdrant storage path |
| `QDRANT_COLLECTION_NAME` | `document_chunks` | Qdrant collection |
| `QDRANT_VECTOR_SIZE` | `1536` | Embedding dimensions |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Allowed frontend origins |

---

## Production Deployment

```bash
# Use PostgreSQL
DATABASE_URL=postgresql://user:password@host:5432/pdf_intelligence

# Set production environment (disables Swagger UI)
APP_ENV=production

# Run with multiple workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```
