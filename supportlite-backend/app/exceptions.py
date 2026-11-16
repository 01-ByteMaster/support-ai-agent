class RAGError(Exception): pass
class DocumentProcessingError(RAGError): pass
class EmbeddingError(RAGError): pass
class RetrievalError(RAGError): pass
class GenerationError(RAGError): pass
