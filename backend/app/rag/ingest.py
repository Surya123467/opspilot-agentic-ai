from pathlib import Path
from sqlalchemy import delete
from app.core.config import settings
from app.db.session import SessionLocal
from app.rag.vector_store import RagDocument, ensure_vector_schema
from langchain_openai import OpenAIEmbeddings

KB_DIR = Path(__file__).resolve().parents[2] / "data" / "knowledge_base"
CHUNK_SIZE = 900
CHUNK_OVERLAP = 120

def chunks(text: str):
    start = 0
    while start < len(text):
        end = min(len(text), start + CHUNK_SIZE)
        piece = text[start:end].strip()
        if piece:
            yield piece
        if end == len(text): break
        start = end - CHUNK_OVERLAP

def main():
    if not settings.openai_api_key:
        raise SystemExit("OPENAI_API_KEY is required to build vector embeddings. Set it in .env and restart the backend.")
    ensure_vector_schema()
    embeddings = OpenAIEmbeddings(model=settings.embedding_model, api_key=settings.openai_api_key)
    records = []
    for path in sorted(KB_DIR.glob("*.md")):
        for idx, content in enumerate(chunks(path.read_text(encoding="utf-8"))):
            records.append((path.name, idx, content))
    vectors = embeddings.embed_documents([r[2] for r in records])
    with SessionLocal() as db:
        db.execute(delete(RagDocument))
        for (source, idx, content), vector in zip(records, vectors):
            db.add(RagDocument(source=source, chunk_index=idx, content=content, embedding=vector))
        db.commit()
    print(f"Indexed {len(records)} chunks from {len(list(KB_DIR.glob('*.md')))} knowledge-base files into pgvector.")

if __name__ == "__main__": main()
