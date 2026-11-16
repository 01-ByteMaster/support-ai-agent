
from app.schemas import RAGQuery, RAGResponse
from app.services.retrieval import retrieve
from app.services.llm_service import generate_answer
from app.exceptions import RetrievalError, GenerationError


ABSTENTION = (
    "I couldn't find sufficient information in the available support "
    "documentation to answer reliably. Please contact a support "
    "representative for clarification."
)


class RAGService:

    async def query(self, request: RAGQuery) -> RAGResponse:

        # --------------------------------------------------
        # 1. Retrieve relevant knowledge chunks
        # --------------------------------------------------
        try:
            chunks = retrieve(
                request.query,
                request.top_k,
                request.metadata_filters
            )

        except RetrievalError:
            return RAGResponse(
                answer="Knowledge retrieval is temporarily unavailable. "
                      "Please try again.",
                status="retrieval_failed",
                reason="retrieval_error",
                follow_up_required=True
            )

        # --------------------------------------------------
        # 2. Handle insufficient evidence
        # --------------------------------------------------
        if not chunks:
            return RAGResponse(
                answer=ABSTENTION,
                status="insufficient_evidence",
                insufficient_context=True,
                reason="no_relevant_evidence",
                follow_up_required=True
            )

        # --------------------------------------------------
        # 3. Construct context from retrieved chunks
        # --------------------------------------------------
        context = "\n\n".join(
            chunk.content for chunk in chunks
        )

        # --------------------------------------------------
        # 4. Generate answer using LLM service
        # --------------------------------------------------
        try:
            answer = await generate_answer(
                query=request.query,
                context=context
            )

        except GenerationError:
            return RAGResponse(
                answer=(
                    "Relevant sources were found, but answer generation "
                    "is temporarily unavailable."
                ),
                status="generation_failed",
                sources=[chunk.source for chunk in chunks],
                reason="generation_error",
                follow_up_required=True
            )

        # --------------------------------------------------
        # 5. Return successful response
        # --------------------------------------------------
        return RAGResponse(
            answer=answer,
            status="answered",
            sources=[chunk.source for chunk in chunks],
            insufficient_context=False,
            follow_up_required=False
        )
