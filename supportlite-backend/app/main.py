from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from app.api import router
from app.database import init_db,engine
from app.config import settings
from sqlalchemy import text
from app.api.openai_compat import router as openai_router


app=FastAPI(title="SupportLite RAG",version="0.1.0")
app.include_router(router)
@app.on_event("startup")
def startup():init_db()
@app.get("/health")
def health():
    try:
        with engine.connect() as c:c.execute(text("SELECT 1"))
        return {"service":"supportlite-rag","status":"ok","database":"ok"}
    except Exception:return {"service":"supportlite-rag","status":"degraded","database":"unavailable"}

app.include_router(openai_router)
