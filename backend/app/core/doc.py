import uuid
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base

class Doc(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name_of_file: Mapped[str] = mapped_column(String(255),unique=True)
    group_number : Mapped[int] = mapped_column(index=True)
    summary : Mapped[str | None] = mapped_column(String(2000))
