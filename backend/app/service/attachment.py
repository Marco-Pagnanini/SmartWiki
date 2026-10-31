import uuid
from dataclasses import dataclass
import io
from pypdf import PdfReader


@dataclass(frozen=True)
class Attachment:
    """A file uploaded in the chat, already converted to text."""
    filename: str
    text: str

_attachments: dict[str, Attachment] = {}


def extract_text(filename: str, data: bytes) -> str:
    """Extract text from a file, based on its extension."""
    if filename.endswith((".pdf", ".PDF")):
        return extract_text_from_pdf(data)
    elif filename.endswith((".docx", ".DOCX")):
        return extract_text_from_docx(data)
    elif filename.endswith((".txt", ".TXT")):
        return data.decode("utf-8")
    else:
        raise ValueError(f"Unsupported file type: {filename}")

def save_attachment(filename: str, text: str) -> str:
    """Store the text of an uploaded file and return its attachment id."""
    attachment_id = uuid.uuid4().hex
    _attachments[attachment_id] = Attachment(filename=filename, text=text)
    return attachment_id

def get_attachment(attachment_id: str) -> Attachment | None:
    """Return the attachment with the given id, or None if it does not exist."""
    return _attachments.get(attachment_id)

def extract_text_from_pdf(data: bytes) -> str:
    """Extract the text of every page of a PDF."""
    reader = PdfReader(io.BytesIO(data))
    return "\n\n".join(page.extract_text() for page in reader.pages)
