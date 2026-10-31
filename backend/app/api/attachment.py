from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel

from app.service.attachment import extract_text, save_attachment

router = APIRouter(prefix="/api/attachments", tags=["attachments"])

MAX_BYTES = 10 * 1024 * 1024  # 10 MB, same limit as nginx


class AttachmentResponse(BaseModel):
    attachment_id: str
    filename: str


@router.post("", response_model=AttachmentResponse)
async def upload_attachment(file: UploadFile) -> AttachmentResponse:
    """Receive a file, extract its text and keep it for the agents."""
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 10 MB)")

    filename = file.filename or "unnamed"
    try:
        text = extract_text(filename, data)
    except (ValueError, UnicodeDecodeError) as e:
        raise HTTPException(status_code=422, detail=str(e))

    attachment_id = save_attachment(filename, text)
    return AttachmentResponse(attachment_id=attachment_id, filename=filename)
