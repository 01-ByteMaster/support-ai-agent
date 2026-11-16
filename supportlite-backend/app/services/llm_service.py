

import os
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b"
)


async def generate_answer(
    query: str,
    context: str,
) -> str:
    response = await client.chat.completions.create(
        model=MODEL,
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content": """
You are SupportLite AI, a customer-support assistant.

Rules:
- Answer using the supplied knowledge context.
- Do not invent company policies.
- Never promise refunds, approvals, or timelines
  unless the context explicitly supports them.
- If the context is insufficient, say so clearly.
- Be professional, concise, and helpful.
"""
            },
            {
                "role": "user",
                "content": f"""
Knowledge Context:
{context}

Customer Question:
{query}

Provide a grounded customer-support answer.
"""
            }
        ]
    )

    return response.choices[0].message.content or ""
