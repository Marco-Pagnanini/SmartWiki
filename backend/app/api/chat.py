from typing import Literal

import anthropic
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents import orchestrator
from app.core.config import settings

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatMessage(BaseModel):
    """A message already exchanged in the chat."""

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)
    attachment_id: str | None = None


class ChatRequest(BaseModel):
    """The user's new message plus the chat history."""

    message: str = Field(min_length=1, max_length=4000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=50)
    attachment_id: str | None = None


class ChatResponse(BaseModel):
    reply: str


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Send the message to the orchestrator and return its answer."""
    if not settings.ANTHROPIC_API_KEY:
        raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY is not set in the .env file")
    try:
        reply = await orchestrator.run(
            request.message,
            history=[m.model_dump() for m in request.history],
            attachment_id=request.attachment_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except anthropic.APIError as e:
        raise HTTPException(status_code=502, detail=f"Claude API error: {e.message}")
    return ChatResponse(reply=reply)
