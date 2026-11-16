from sqlalchemy import delete
from app.database import SessionLocal
from app.models import KnowledgeChunk
from app.services.document_loader import load_directory
from app.services.chunking import split_document
from app.services.embeddings import embed_texts
from app.schemas import IngestResponse
def ingest_directory(directory):
    docs=load_directory(directory);processed=skipped=failed=count=0;errors=[]
    for doc in docs:
        try:
            chunks=split_document(doc)
            if not chunks:skipped+=1;continue
            vectors=embed_texts([c.page_content for c in chunks])
            with SessionLocal() as db:
                db.execute(delete(KnowledgeChunk).where(KnowledgeChunk.document_id==doc.metadata["document_id"]))
                for c,v in zip(chunks,vectors):
                    m=dict(c.metadata);db.add(KnowledgeChunk(document_id=m["document_id"],chunk_id=m["chunk_id"],chunk_index=m["chunk_index"],content=c.page_content,embedding=v,metadata_json=m,content_hash=m["content_hash"]))
                db.commit()
            processed+=1;count+=len(chunks)
        except Exception as e:
            failed+=1;errors.append(f'{doc.metadata.get("document_id","unknown")}: {type(e).__name__}')
    return IngestResponse(discovered=len(docs),processed=processed,skipped=skipped,failed=failed,chunks=count,errors=errors)
