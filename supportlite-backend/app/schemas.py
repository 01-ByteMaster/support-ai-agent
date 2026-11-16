from typing import Any
from pydantic import BaseModel,Field
class RAGQuery(BaseModel):
    query:str=Field(min_length=2,max_length=2000)
    top_k:int=Field(default=5,ge=1,le=20)
    metadata_filters:dict[str,Any]=Field(default_factory=dict)
class Source(BaseModel):
    document_id:str
    document_title:str
    chunk_id:str
    section:str|None=None
    page_number:int|None=None
    score:float
class RAGResponse(BaseModel):
    answer:str
    status:str
    sources:list[Source]=Field(default_factory=list)
    confidence:float|None=None
    insufficient_context:bool=False
    reason:str|None=None
    follow_up_required:bool=False
class RetrievedChunk(BaseModel):
    content:str
    source:Source
    metadata:dict[str,Any]=Field(default_factory=dict)
class IngestResponse(BaseModel):
    discovered:int
    processed:int
    skipped:int
    failed:int
    chunks:int
    errors:list[str]=Field(default_factory=list)
