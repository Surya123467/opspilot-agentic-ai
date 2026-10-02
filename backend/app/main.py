from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.runs import router as runs_router
from app.core.config import settings
from app.db.session import init_db
from app.rag.vector_store import ensure_vector_schema
app=FastAPI(title="OpsPilot Agentic AI API",version="1.0.0",description="Enterprise Agentic AI operations assistant.")
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in settings.cors_origins.split(",")],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(runs_router)
@app.on_event("startup")
def startup():
    init_db()
    ensure_vector_schema()
@app.get("/health")
def health():
    return {"status":"ok","service":"opspilot-api","mock_mode":settings.mock_mode,"vector_store":"pgvector","embedding_model":settings.embedding_model,"embeddings_configured":bool(settings.openai_api_key)}
