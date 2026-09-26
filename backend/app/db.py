"""
DB engine + session setup.

Defaults to a local SQLite file for fast dev/testing without needing
Postgres running. For real deployment, set DATABASE_URL, e.g.:
    postgresql+psycopg://trustgraph:trustgraph@localhost:5432/trustgraph
(note the +psycopg — this project uses psycopg3, not psycopg2)
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./coven.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Call once on startup."""
    import app.models  # noqa: ensures Case/Evidence/Event are registered
    Base.metadata.create_all(bind=engine)
