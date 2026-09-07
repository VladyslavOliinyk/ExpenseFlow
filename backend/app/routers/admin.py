from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models import AiCallLog, Claim, User
from app.schemas import AiMetrics

router = APIRouter()


@router.get("/admin/ai-metrics")
def ai_metrics(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> AiMetrics:
    # analyzed_count = claims with a completed AI result (the canonical denominator).
    # Previously total_analyzed was AiCallLog success count, which differs from
    # analyzed_count when retries/fallbacks occur (multiple log rows per claim),
    # causing mismatch_rate to divide by a different number than what the UI showed.
    analyzed_count = db.query(Claim).filter(Claim.ai_summary.isnot(None)).count()

    mismatch_count = (
        db.query(Claim)
        .filter(Claim.ai_mismatch_flag == True)  # noqa: E712
        .count()
    )
    mismatch_rate = (mismatch_count / analyzed_count) if analyzed_count > 0 else 0.0

    avg_latency = db.query(func.avg(AiCallLog.latency_ms)).scalar()

    provider_rows = (
        db.query(AiCallLog.provider, func.count(AiCallLog.id))
        .filter(AiCallLog.success == True)  # noqa: E712
        .group_by(AiCallLog.provider)
        .all()
    )
    provider_breakdown = {row[0]: row[1] for row in provider_rows}

    return AiMetrics(
        total_analyzed=analyzed_count,
        mismatch_count=mismatch_count,
        mismatch_rate=round(mismatch_rate, 3),
        avg_latency_ms=round(float(avg_latency), 1) if avg_latency else None,
        provider_breakdown=provider_breakdown,
    )
