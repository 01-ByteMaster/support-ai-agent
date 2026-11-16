
import json
import os
import time
import uuid

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse


router = APIRouter(
    prefix="/v1",
    tags=["OpenAI Compatibility"]
)

RAG_URL = "http://127.0.0.1:8000/api/v1/rag/query"
MODEL_ID = "supportlite-rag"
RAG_TOP_K = 5


# ============================================================
# 1. Authentication
# ============================================================

def authenticate(request: Request):
    expected = os.getenv("SUPPORTLITE_UI_API_KEY", "")
    actual = request.headers.get("Authorization", "")

    if not expected or actual != f"Bearer {expected}":
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )


# ============================================================
# 2. OpenAI-compatible models endpoint
# ============================================================

@router.get("/models")
async def models(request: Request):

    authenticate(request)

    return {
        "object": "list",
        "data": [
            {
                "id": MODEL_ID,
                "object": "model",
                "created": int(time.time()),
                "owned_by": "supportlite"
            }
        ]
    }


# ============================================================
# 3. Extract latest user query
# ============================================================

def extract_user_query(messages: list) -> str:

    user_messages = [
        message
        for message in messages
        if isinstance(message, dict)
        and message.get("role") == "user"
    ]

    if not user_messages:
        raise HTTPException(
            status_code=400,
            detail="User message is required"
        )

    content = user_messages[-1].get("content", "")

    # Standard text message
    if isinstance(content, str):
        query = content

    # Multimodal message content
    elif isinstance(content, list):
        query = " ".join(
            item.get("text", "")
            for item in content
            if isinstance(item, dict)
            and item.get("type") == "text"
        )

    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported user message content"
        )

    query = query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="User message cannot be empty"
        )

    return query


# ============================================================
# 4. Format retrieved sources
# ============================================================

def format_sources(sources: list) -> str:

    if not sources:
        return ""

    names = []

    for source in sources:

        if isinstance(source, str):
            name = source

        elif isinstance(source, dict):
            name = (
                source.get("document_title")
                or source.get("source")
                or source.get("filename")
                or source.get("file_name")
                or "Unknown"
            )

        else:
            name = "Unknown"

        if name and name not in names:
            names.append(name)

    if not names:
        return ""

    return "\n\nSources: " + ", ".join(names)


# ============================================================
# 5. Call SupportLite RAG backend
# ============================================================

async def call_rag(query: str) -> dict:

    timeout = httpx.Timeout(
        120.0,
        connect=10.0
    )

    try:
        async with httpx.AsyncClient(
            timeout=timeout
        ) as client:

            response = await client.post(
                RAG_URL,
                json={
                    "query": query,
                    "top_k": RAG_TOP_K,
                    "metadata_filters": {}
                }
            )

            response.raise_for_status()

            result = response.json()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="SupportLite RAG request timed out"
        )

    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail="SupportLite RAG returned an upstream error"
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="SupportLite RAG service unavailable"
        )

    except ValueError:
        raise HTTPException(
            status_code=502,
            detail="Invalid JSON response from SupportLite RAG"
        )

    if not isinstance(result, dict):
        raise HTTPException(
            status_code=502,
            detail="Invalid response format from SupportLite RAG"
        )

    return result


# ============================================================
# 6. OpenAI-compatible Chat Completion endpoint
# ============================================================

@router.post("/chat/completions")
async def chat_completions(
    request: Request,
    body: dict
):

    authenticate(request)

    # --------------------------------------------------------
    # Validate request
    # --------------------------------------------------------

    messages = body.get("messages", [])

    if not isinstance(messages, list):
        raise HTTPException(
            status_code=400,
            detail="messages must be a list"
        )

    query = extract_user_query(messages)

    # --------------------------------------------------------
    # Call RAG
    # --------------------------------------------------------

    result = await call_rag(query)

    answer = result.get("answer")

    if not isinstance(answer, str) or not answer.strip():
        raise HTTPException(
            status_code=502,
            detail="Empty response from SupportLite RAG"
        )

    # --------------------------------------------------------
    # Append source information
    # --------------------------------------------------------

    sources = result.get("sources", [])

    if isinstance(sources, list):
        answer += format_sources(sources)

    # --------------------------------------------------------
    # Completion metadata
    # --------------------------------------------------------

    completion_id = f"chatcmpl-{uuid.uuid4().hex}"
    created = int(time.time())

    # --------------------------------------------------------
    # Non-streaming response
    # --------------------------------------------------------

    if not body.get("stream", False):

        return {
            "id": completion_id,
            "object": "chat.completion",
            "created": created,
            "model": MODEL_ID,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": answer
                    },
                    "finish_reason": "stop"
                }
            ]
        }

    # --------------------------------------------------------
    # Streaming response
    # --------------------------------------------------------

    async def generate():

        # First chunk
        chunk = {
            "id": completion_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": MODEL_ID,
            "choices": [
                {
                    "index": 0,
                    "delta": {
                        "role": "assistant",
                        "content": answer
                    },
                    "finish_reason": None
                }
            ]
        }

        yield f"data: {json.dumps(chunk)}\n\n"

        # Final chunk
        final_chunk = {
            "id": completion_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": MODEL_ID,
            "choices": [
                {
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop"
                }
            ]
        }

        yield f"data: {json.dumps(final_chunk)}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
