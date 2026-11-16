from sqlalchemy import select
from app.database import SessionLocal
from app.models import KnowledgeChunk
from app.services.embeddings import embed_query
from app.schemas import RetrievedChunk,Source
from app.config import settings
from app.exceptions import RetrievalError
def retrieve(query,top_k=5,metadata_filters=None):
    if not query.strip():raise RetrievalError("Empty query")
    try:
        vec=embed_query(query);dist=KnowledgeChunk.embedding.cosine_distance(vec)
        stmt=select(KnowledgeChunk,dist.label("distance")).order_by(dist).limit(top_k)
        with SessionLocal() as db:rows=db.execute(stmt).all()
        out=[]
        for row,d in rows:
            score=max(0.,min(1.,1-float(d)));meta=row.metadata_json or {}
            if metadata_filters and any(meta.get(k)!=v for k,v in metadata_filters.items()):continue
            if score<settings.rag_min_similarity:continue
            src=Source(document_id=row.document_id,document_title=meta.get("document_title",row.document_id),chunk_id=row.chunk_id,section=meta.get("section"),page_number=meta.get("page_number"),score=score)
            out.append(RetrievedChunk(content=row.content,source=src,metadata=meta))
        return out
    except RetrievalError:raise
    except Exception as e:raise RetrievalError("Vector retrieval failed") from e
