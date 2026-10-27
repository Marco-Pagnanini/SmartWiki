from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
def health() -> dict:
    """Verifica che il backend sia attivo."""
    return {"status": "ok", "app": settings.APP_NAME}


@router.get("/db")
def health_db(db: Session = Depends(get_db)):
    """Verifica che il database risponda eseguendo SELECT 1."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "database": "unreachable"},
        )
    return {"status": "ok", "database": "connected"}
