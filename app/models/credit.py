import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String, DateTime, Uuid, ForeignKey
from app.database import Base

class Credit(Base):
    __tablename__ = "credits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), unique=True) 
    balance: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.utcnow)

class CreditTransaction(Base):
    __tablename__ = "credit_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"))
    amount: Mapped[int] = mapped_column(Integer)
    transaction_type: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))