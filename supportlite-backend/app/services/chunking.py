from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import settings
def split_document(doc):
    splitter=RecursiveCharacterTextSplitter(chunk_size=settings.chunk_size,chunk_overlap=settings.chunk_overlap,separators=["\\n\\n","\\n",". "," ",""],add_start_index=True)
    chunks=splitter.split_documents([doc])
    for i,c in enumerate(chunks):
        c.metadata["chunk_index"]=i;c.metadata["chunk_id"]=f'{doc.metadata["document_id"]}:{i}'
    return chunks
