
from sqlalchemy.orm import Session
from app.core.doc import Doc
import uuid
from sqlalchemy import select

def create_doc(db:Session, name_of_file:str, group_number:int,summary:str | None=None) -> Doc:
    """Create a document and save in the database"""
    doc = Doc(name_of_file=name_of_file, group_number=group_number, summary=summary)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def get_doc(db: Session, doc_id: uuid.UUID) -> Doc | None:
    """Return the document with the given id, or None if it does not exist."""
    return db.get(Doc, doc_id)

def get_doc_by_name(db:Session, name_of_file:str) -> Doc | None:
    query = select(Doc).where(Doc.name_of_file == name_of_file)
    return db.scalars(query).one_or_none()
def get_all_docs(db:Session) -> list[Doc]:
    query = select(Doc)
    return db.scalars(query).all()
