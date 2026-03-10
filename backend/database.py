from typing import Annotated
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from fastapi import Depends
from models import Base          # absolute import (backend/ is the root)

DATABASE_URL = "sqlite:///./taskmate.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")
    print("Tables created successfully")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── Reusable dependency annotation ──────────────────────────────────────────
# Example:
#   def my_route(db: DbSession): ...
DbSession = Annotated[Session, Depends(get_db)]