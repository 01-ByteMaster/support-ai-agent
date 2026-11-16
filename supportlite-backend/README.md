# SupportLite AI — Module 4 RAG

Standalone customer-support RAG service: FastAPI + LangChain + PostgreSQL/pgvector + Sentence Transformers + optional Gemini.

## Quick start
1. `docker compose up -d db`
2. `copy .env.example .env` (Windows) and add `GEMINI_API_KEY` if desired.
3. `python -m venv .venv`; activate it; `pip install -r requirements.txt`
4. `python -m app.cli ingest`
5. `uvicorn app.main:app --reload`
6. API docs: http://localhost:8000/docs

## Endpoints
- `GET /health`
- `POST /api/v1/rag/query`
- `POST /api/v1/rag/retrieve` (debug; protect/disable in production)
- `POST /api/v1/rag/ingest` (admin token)
- `GET /api/v1/rag/documents` (admin token)

## Orchestrator integration
```python
from app.services.rag_service import RAGService
from app.schemas import RAGQuery
rag = RAGService()
result = await rag.query(RAGQuery(query="What is the refund policy?"))
# Send result through your guardrails before displaying it.
if result.status != "answered":
    # ask clarification or escalate to human support
    ...
```

Sample documents are DEMONSTRATION DATA, not actual company policy. Similarity is not factual proof. Production needs auth, rate limits, PII controls, monitoring, backups, and approved policy lifecycle.
