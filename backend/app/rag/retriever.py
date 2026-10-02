from pathlib import Path
from sqlalchemy import select
from app.core.config import settings
from app.db.session import SessionLocal
from app.rag.vector_store import RagDocument, ensure_vector_schema

KB_DIR = Path(__file__).resolve().parents[2] / "data" / "knowledge_base"

class KnowledgeRetriever:
    def __init__(self):
        self.enabled = False
        self.embeddings = None
        ensure_vector_schema()
        if settings.openai_api_key:
            try:
                from langchain_openai import OpenAIEmbeddings
                self.embeddings = OpenAIEmbeddings(
                    model=settings.embedding_model,
                    api_key=settings.openai_api_key,
                )
                self.enabled = True
            except Exception:
                self.enabled = False

    def search(self, query: str, k: int = 4):
        if not self.enabled:
            return self._keyword_fallback(query, k)
        vector = self.embeddings.embed_query(query)
        with SessionLocal() as db:
            rows = db.scalars(
                select(RagDocument)
                .where(RagDocument.embedding.is_not(None))
                .order_by(RagDocument.embedding.cosine_distance(vector))
                .limit(k)
            ).all()
            return [
                {"source": r.source, "chunk_index": r.chunk_index, "text": r.content,
                 "score": None, "retrieval": "pgvector-cosine"}
                for r in rows
            ]

    def _keyword_fallback(self, query: str, k: int):
        terms = {x.lower() for x in query.split() if len(x) > 2}
        scored = []
        for path in KB_DIR.glob("*.md") if KB_DIR.exists() else []:
            text = path.read_text(encoding="utf-8")
            score = sum(text.lower().count(term) for term in terms)
            scored.append((score, path.name, text))
        scored.sort(reverse=True)
        return [{"source": s, "chunk_index": 0, "text": t, "score": score, "retrieval": "keyword-fallback"}
                for score, s, t in scored[:k]]

retriever = KnowledgeRetriever()
