from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.models.claim import AiStatus, ClaimStatus
from app.schemas.category import CategoryOut
from app.schemas.user import UserOut


class ClaimCreate(BaseModel):
    category_id: int
    amount: Decimal = Field(gt=0)
    description: str
    expense_date: date
    payment_details: str = Field(max_length=200)

    @field_validator("expense_date")
    @classmethod
    def not_in_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Expense date cannot be in the future")
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
    ai_status: AiStatus
    ai_summary: str | None
    ai_mismatch_flag: bool | None
    ai_mismatch_reason: str | None
    ai_provider_used: str | None
    is_potential_duplicate: bool
    duplicate_of_claim_id: int | None
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
