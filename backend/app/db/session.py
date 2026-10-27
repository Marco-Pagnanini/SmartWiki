from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# pool_pre_ping verifica che la connessione sia ancora valida prima di usarla
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    """Classe base per i modelli SQLAlchemy (verranno aggiunti in seguito)."""


def get_db() -> Generator[Session, None, None]:
    """Dependency FastAPI: apre una sessione e la chiude a fine richiesta."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
