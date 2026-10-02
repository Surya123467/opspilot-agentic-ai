from sqlalchemy import text
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Text as SqlText
from app.db.session import Base, engine

EMBEDDING_DIM = 1536

class RagDocument(Base):
    __tablename__ = "rag_documents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(255), index=True)
    chunk_index: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(SqlText)
    embedding = mapped_column(Vector(EMBEDDING_DIM))

def ensure_vector_schema():
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)
