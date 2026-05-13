import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# On Vercel (serverless) the only writable path is /tmp.
# Locally we keep the DB next to the project so data persists between runs.
def _resolve_db_path() -> Path:
    if os.environ.get("VERCEL"):
        return Path("/tmp/wilson_inventory.db")
    return Path(__file__).resolve().parent.parent / "wilson_inventory.db"


DB_PATH = _resolve_db_path()
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
