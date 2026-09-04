from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, field_validator

from app.models.claim import ClaimStatus
from app.schemas.category import CategoryOut
from app.schemas.user import UserOut


class ClaimCreate(BaseModel):
    category_id: int
    amount: Decimal
    description: str
    expense_date: date
    payment_details: str

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v

    @field_validator("description", "payment_details")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v


class ClaimOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    requester_id: int
    category_id: int
    amount: Decimal
    description: str
    expense_date: date
    payment_details: str
    status: ClaimStatus
    reject_comment: str | None
    ai_summary: str | None
    ai_mismatch_flag: bool | None
    ai_mismatch_reason: str | None
    ai_provider_used: str | None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None
    requester: UserOut | None = None
    category: CategoryOut | None = None


class RejectBody(BaseModel):
    comment: str

    @field_validator("comment")
    @classmethod
    def comment_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Reject comment cannot be empty")
        return v
