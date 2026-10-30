from typing import Literal

import anthropic
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents import orchestrator
from app.core.config import settings

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatMessage(BaseModel):
    """Un messaggio già scambiato nella chat."""

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    """Il nuovo messaggio dell'utente più la cronologia della chat."""

    message: str = Field(min_length=1, max_length=4000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=50)


class ChatResponse(BaseModel):
    reply: str


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Invia il messaggio all'orchestrator e restituisce la sua risposta."""
    if not settings.ANTHROPIC_API_KEY:
        raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY non configurata nel file .env")
    try:
        reply = await orchestrator.run(
            request.message,
            history=[m.model_dump() for m in request.history],
        )
    except anthropic.APIError as e:
        raise HTTPException(status_code=502, detail=f"Errore dell'API di Claude: {e.message}")
    return ChatResponse(reply=reply)
