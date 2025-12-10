import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String, DateTime, Uuid, ForeignKey # Aggiunto ForeignKey
from app.database import Base

class Conversion(Base):
    __tablename__ = "conversions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False)
    source_format: Mapped[str] = mapped_column(String(20)) 
    target_format: Mapped[str] = mapped_column(String(20))
    input_size_bytes: Mapped[int] = mapped_column(Integer) # Corretto str -> int nel type hint
    credits_used: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20))
    error_message: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))