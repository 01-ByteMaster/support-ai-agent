from sqlalchemy import String,Text,Integer,DateTime,JSON,UniqueConstraint,func
from sqlalchemy.orm import Mapped,mapped_column
from pgvector.sqlalchemy import Vector
from app.database import Base
from app.config import settings
class KnowledgeChunk(Base):
    __tablename__="knowledge_chunks"
    __table_args__=(UniqueConstraint("document_id","chunk_index",name="uq_doc_chunk_index"),)
    id:Mapped[int]=mapped_column(primary_key=True)
    document_id:Mapped[str]=mapped_column(String(200),index=True)
    chunk_id:Mapped[str]=mapped_column(String(300),unique=True,index=True)
    chunk_index:Mapped[int]=mapped_column(Integer)
    content:Mapped[str]=mapped_column(Text)
    embedding:Mapped[list]=mapped_column(Vector(settings.embedding_dimensions))
    metadata_json:Mapped[dict]=mapped_column("metadata",JSON,default=dict)
    content_hash:Mapped[str]=mapped_column(String(64),index=True)
    created_at:Mapped[object]=mapped_column(DateTime(timezone=True),server_default=func.now())
    updated_at:Mapped[object]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
