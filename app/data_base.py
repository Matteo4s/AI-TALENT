import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:mAtvey2277@localhost:5432/talent_ai",
)

def _build_engine():
    try:
        candidate_engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        with candidate_engine.connect():
            pass
        return candidate_engine
    except (UnicodeDecodeError, SQLAlchemyError):
        fallback_url = "sqlite:///./talent_ai.db"
        return create_engine(fallback_url, connect_args={"check_same_thread": False})


engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()