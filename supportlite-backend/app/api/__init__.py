
from fastapi import APIRouter,Header,HTTPException,Depends
from app.config import settings
from app.schemas import RAGQuery,RAGResponse,IngestResponse
from app.services.rag_service import RAGService
from app.services.retrieval import retrieve
from app.services.ingestion import ingest_directory

router=APIRouter(prefix="/api/v1/rag",tags=["RAG"]);service=RAGService()
def require_admin(x_admin_token:str|None=Header(default=None)):
    if not x_admin_token or x_admin_token!=settings.admin_api_token:raise HTTPException(401,"Unauthorized")

@router.post("/query",response_model=RAGResponse)
async def query(request:RAGQuery):return await service.query(request)

@router.post("/retrieve")
def debug_retrieve(request:RAGQuery):return retrieve(request.query,request.top_k,request.metadata_filters)

@router.post("/ingest",response_model=IngestResponse,dependencies=[Depends(require_admin)])
def ingest():return ingest_directory(settings.knowledge_base_path)

@router.get("/documents",dependencies=[Depends(require_admin)])
def documents():
    from sqlalchemy import select,distinct
    from app.database import SessionLocal
    from app.models import KnowledgeChunk
    with SessionLocal() as db:return {"document_ids":db.execute(select(distinct(KnowledgeChunk.document_id))).scalars().all()}
