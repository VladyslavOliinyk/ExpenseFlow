import hashlib
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.ai.prompts import PROMPT_VERSION
from app.dependencies import get_current_user, get_db
from app.models import Category, Claim, User
from app.models.claim import ClaimStatus
from app.schemas import ClaimCreate, ClaimOut, RejectBody

router = APIRouter()


def _compute_hash(amount, category_id: int, description: str) -> str:
    raw = f"{amount}:{category_id}:{description.strip().lower()}|v{PROMPT_VERSION}"
    return hashlib.sha256(raw.encode()).hexdigest()


def _claim_to_out(claim: Claim) -> ClaimOut:
    from app.schemas.user import UserOut
    from app.schemas.category import CategoryOut

    requester_out = UserOut(
        id=claim.requester.id,
        name=claim.requester.name,
        email=claim.requester.email,
        managed_category_ids=[c.id for c in claim.requester.managed_categories],
        managed_category_names=[c.name for c in claim.requester.managed_categories],
    ) if claim.requester else None

    category_out = CategoryOut(
        id=claim.category.id,
        name=claim.category.name,
        responsible_manager_id=claim.category.responsible_manager_id,
    ) if claim.category else None

    return ClaimOut(
        id=claim.id,
        requester_id=claim.requester_id,
        category_id=claim.category_id,
        amount=claim.amount,
        description=claim.description,
        expense_date=claim.expense_date,
        payment_details=claim.payment_details,
        status=claim.status,
        reject_comment=claim.reject_comment,
        ai_summary=claim.ai_summary,
        ai_mismatch_flag=claim.ai_mismatch_flag,
        ai_mismatch_reason=claim.ai_mismatch_reason,
        ai_provider_used=claim.ai_provider_used,
        created_at=claim.created_at,
        updated_at=claim.updated_at,
        resolved_at=claim.resolved_at,
        requester=requester_out,
        category=category_out,
    )


@router.post("/claims", status_code=201)
def create_claim(
    body: ClaimCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClaimOut:
    category = db.query(Category).filter(Category.id == body.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    content_hash = _compute_hash(body.amount, body.category_id, body.description)

    claim = Claim(
        requester_id=current_user.id,
        category_id=body.category_id,
        amount=body.amount,
        description=body.description,
        expense_date=body.expense_date,
        payment_details=body.payment_details,
        content_hash=content_hash,
    )
    db.add(claim)
    db.commit()
    db.refresh(claim)

    # Eager-load relationships for response
    claim = (
        db.query(Claim)
        .options(
            joinedload(Claim.requester).joinedload(User.managed_categories),
            joinedload(Claim.category),
        )
        .filter(Claim.id == claim.id)
        .first()
    )

    background_tasks.add_task(_run_ai_analysis, claim.id)

    return _claim_to_out(claim)


def _run_ai_analysis(claim_id: int):
    """Background task: run AI analysis and save results to the claim."""
    import logging
    from app.ai.router import analyze_claim_with_fallback

    logger = logging.getLogger(__name__)
    db = SessionLocal_bg()
    try:
        claim = (
            db.query(Claim)
            .options(joinedload(Claim.category))
            .filter(Claim.id == claim_id)
            .first()
        )
        if not claim:
            return

        # Check dedup: same content_hash with AI results already
        if claim.content_hash:
            existing = (
                db.query(Claim)
                .filter(
                    Claim.content_hash == claim.content_hash,
                    Claim.ai_summary.isnot(None),
                    Claim.id != claim.id,
                )
                .first()
            )
            if existing:
                claim.ai_summary = existing.ai_summary
                claim.ai_mismatch_flag = existing.ai_mismatch_flag
                claim.ai_mismatch_reason = existing.ai_mismatch_reason
                claim.ai_provider_used = f"cached:{existing.ai_provider_used}"
                db.commit()
                return

        result = analyze_claim_with_fallback(
            claim_id=claim.id,
            amount=float(claim.amount),
            category=claim.category.name,
            description=claim.description,
            db=db,
        )
        if result:
            claim.ai_summary = result.summary
            claim.ai_mismatch_flag = result.mismatch_flag
            claim.ai_mismatch_reason = result.mismatch_reason
            claim.ai_provider_used = result.provider_used
            db.commit()
    except Exception:
        logger.exception("AI background analysis failed for claim_id=%s", claim_id)
        # ai_summary stays None — frontend shows "AI insight unavailable"
        try:
            db.rollback()
        except Exception:
            pass
    finally:
        db.close()


# Lazy import to avoid circular at module load time
def SessionLocal_bg():
    from app.database import SessionLocal
    return SessionLocal()


@router.get("/claims/mine")
def my_claims(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ClaimOut]:
    claims = (
        db.query(Claim)
        .options(
            joinedload(Claim.requester).joinedload(User.managed_categories),
            joinedload(Claim.category),
        )
        .filter(Claim.requester_id == current_user.id)
        .order_by(Claim.created_at.desc())
        .all()
    )
    return [_claim_to_out(c) for c in claims]


@router.get("/claims/queue")
def manager_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ClaimOut]:
    """Claims pending review for categories managed by current user."""
    managed_ids = [c.id for c in current_user.managed_categories]
    if not managed_ids:
        return []

    claims = (
        db.query(Claim)
        .options(
            joinedload(Claim.requester).joinedload(User.managed_categories),
            joinedload(Claim.category),
        )
        .filter(
            Claim.category_id.in_(managed_ids),
            Claim.status == ClaimStatus.pending,
        )
        .order_by(Claim.created_at.desc())
        .all()
    )
    return [_claim_to_out(c) for c in claims]


@router.get("/claims/{claim_id}")
def get_claim(
    claim_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClaimOut:
    claim = (
        db.query(Claim)
        .options(
            joinedload(Claim.requester).joinedload(User.managed_categories),
            joinedload(Claim.category),
        )
        .filter(Claim.id == claim_id)
        .first()
    )
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    managed_ids = [c.id for c in current_user.managed_categories]
    is_requester = claim.requester_id == current_user.id
    is_manager = claim.category_id in managed_ids

    if not is_requester and not is_manager:
        raise HTTPException(status_code=403, detail="Access denied")

    return _claim_to_out(claim)


@router.post("/claims/{claim_id}/withdraw")
def withdraw_claim(
    claim_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClaimOut:
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    if claim.requester_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your claim")
    if claim.status != ClaimStatus.pending:
        raise HTTPException(status_code=400, detail="Only pending claims can be withdrawn")

    claim.status = ClaimStatus.withdrawn
    claim.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(claim)

    claim = (
        db.query(Claim)
        .options(
            joinedload(Claim.requester).joinedload(User.managed_categories),
            joinedload(Claim.category),
        )
        .filter(Claim.id == claim_id)
        .first()
    )
    return _claim_to_out(claim)


@router.post("/claims/{claim_id}/approve")
def approve_claim(
    claim_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClaimOut:
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    managed_ids = [c.id for c in current_user.managed_categories]
    if claim.category_id not in managed_ids:
        raise HTTPException(status_code=403, detail="Not your category to manage")
    if claim.requester_id == current_user.id:
        raise HTTPException(status_code=403, detail="Cannot approve your own claim")
    if claim.status != ClaimStatus.pending:
        raise HTTPException(status_code=400, detail="Only pending claims can be approved")

    claim.status = ClaimStatus.approved
    claim.resolved_at = datetime.now(timezone.utc)
    db.commit()

    claim = (
        db.query(Claim)
        .options(
            joinedload(Claim.requester).joinedload(User.managed_categories),
            joinedload(Claim.category),
        )
        .filter(Claim.id == claim_id)
        .first()
    )
    return _claim_to_out(claim)


@router.post("/claims/{claim_id}/reject")
def reject_claim(
    claim_id: int,
    body: RejectBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClaimOut:
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    managed_ids = [c.id for c in current_user.managed_categories]
    if claim.category_id not in managed_ids:
        raise HTTPException(status_code=403, detail="Not your category to manage")
    if claim.requester_id == current_user.id:
        raise HTTPException(status_code=403, detail="Cannot reject your own claim")
    if claim.status != ClaimStatus.pending:
        raise HTTPException(status_code=400, detail="Only pending claims can be rejected")

    claim.status = ClaimStatus.rejected
    claim.reject_comment = body.comment
    claim.resolved_at = datetime.now(timezone.utc)
    db.commit()

    claim = (
        db.query(Claim)
        .options(
            joinedload(Claim.requester).joinedload(User.managed_categories),
            joinedload(Claim.category),
        )
        .filter(Claim.id == claim_id)
        .first()
    )
    return _claim_to_out(claim)
