import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ClaimStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    withdrawn = "withdrawn"


class AiStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(primary_key=True)
    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    description: Mapped[str] = mapped_column(Text)
    expense_date: Mapped[date] = mapped_column(Date)
    payment_details: Mapped[str] = mapped_column(Text)

    status: Mapped[ClaimStatus] = mapped_column(
        Enum(ClaimStatus), default=ClaimStatus.pending
    )
    reject_comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    # AI fields
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    ai_status: Mapped[AiStatus] = mapped_column(
        Enum(AiStatus, name="aistatus"), default=AiStatus.pending
    )
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_mismatch_flag: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    ai_mismatch_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_provider_used: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Duplicate detection (SQL-based, not AI)
    is_potential_duplicate: Mapped[bool] = mapped_column(Boolean, default=False)
    duplicate_of_claim_id: Mapped[int | None] = mapped_column(
        ForeignKey("claims.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    requester: Mapped["User"] = relationship("User", back_populates="claims")
    category: Mapped["Category"] = relationship("Category", back_populates="claims")
    ai_call_logs: Mapped[list["AiCallLog"]] = relationship(
        "AiCallLog", back_populates="claim"
    )
