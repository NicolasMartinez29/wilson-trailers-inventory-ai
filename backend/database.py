import os
import shutil
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


BACKEND_DIR = Path(__file__).resolve().parent
BUNDLED_SEED = BACKEND_DIR / "wilson_inventory_seed.db"


def _resolve_db_path() -> Path:
    """
    On Vercel (serverless), copy the pre-seeded SQLite bundle from the
    read-only function dir into /tmp on first invocation. This avoids
    multi-second seed runs that time out cold starts and leave the DB
    half-populated.
    """
    if os.environ.get("VERCEL"):
        target = Path("/tmp/wilson_inventory.db")
        if not target.exists() and BUNDLED_SEED.exists():
            try:
                shutil.copyfile(BUNDLED_SEED, target)
            except Exception:
                pass
        return target
    return BACKEND_DIR.parent / "wilson_inventory.db"


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
