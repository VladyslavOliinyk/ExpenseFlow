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
    total = db.query(AiCallLog).filter(AiCallLog.success == True).count()  # noqa: E712

    mismatch_count = (
        db.query(Claim)
        .filter(Claim.ai_mismatch_flag == True)  # noqa: E712
        .count()
    )
    analyzed_count = db.query(Claim).filter(Claim.ai_summary.isnot(None)).count()
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
        total_analyzed=total,
        mismatch_count=mismatch_count,
        mismatch_rate=round(mismatch_rate, 3),
        avg_latency_ms=round(float(avg_latency), 1) if avg_latency else None,
        provider_breakdown=provider_breakdown,
    )
