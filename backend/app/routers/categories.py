from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models import Category, User
from app.schemas import CategoryOut

router = APIRouter()


@router.get("/categories")
def list_categories(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[CategoryOut]:
    return db.query(Category).order_by(Category.id).all()
