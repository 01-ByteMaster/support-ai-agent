from pathlib import Path
import hashlib,fitz
from docx import Document as WordDocument
from langchain_core.documents import Document
from app.exceptions import DocumentProcessingError
SUPPORTED={".pdf",".txt",".md",".docx"}
def load_file(path:Path)->Document:
    try:
        ext=path.suffix.lower()
        if ext not in SUPPORTED: raise DocumentProcessingError(f"Unsupported extension: {ext}")
        if ext==".pdf":
            with fitz.open(path) as pdf: text="\\n".join(p.get_text("text") for p in pdf)
        elif ext==".docx": text="\\n".join(p.text for p in WordDocument(path).paragraphs)
        else: text=path.read_text(encoding="utf-8")
        text=text.strip()
        if not text: raise DocumentProcessingError("No extractable text (scanned PDF may require OCR)")
        return Document(page_content=text,metadata={"document_id":path.stem,"document_title":path.stem.replace("_"," ").title(),"source":str(path),"file_type":ext[1:],"content_hash":hashlib.sha256(text.encode()).hexdigest(),"version":"1","section":None})
    except DocumentProcessingError: raise
    except Exception as e: raise DocumentProcessingError(f"Could not process {path.name}: {type(e).__name__}") from e
def load_directory(directory:str):
    root=Path(directory)
    if not root.exists(): raise DocumentProcessingError(f"Missing knowledge base: {root}")
    return [load_file(p) for p in sorted(root.rglob("*")) if p.is_file() and p.suffix.lower() in SUPPORTED]
