from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AiCallLog(Base):
    __tablename__ = "ai_call_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    claim_id: Mapped[int] = mapped_column(ForeignKey("claims.id"))
    provider: Mapped[str] = mapped_column(String(50))
    latency_ms: Mapped[int] = mapped_column(Integer)
    success: Mapped[bool] = mapped_column(Boolean)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    claim: Mapped["Claim"] = relationship("Claim", back_populates="ai_call_logs")
