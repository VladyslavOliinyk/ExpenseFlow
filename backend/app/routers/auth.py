from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models import User
from app.schemas import UserOut
from app.services.auth_service import create_access_token

router = APIRouter()


@router.post("/auth/login-as/{user_id}")
def login_as(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/auth/users")
def list_users(db: Session = Depends(get_db)) -> list[UserOut]:
    """Return all users for the demo login switcher."""
    users = db.query(User).order_by(User.id).all()
    return [
        UserOut(
            id=u.id,
            name=u.name,
            email=u.email,
            managed_category_ids=[c.id for c in u.managed_categories],
            managed_category_names=[c.name for c in u.managed_categories],
        )
        for u in users
    ]


@router.get("/me")
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        managed_category_ids=[c.id for c in current_user.managed_categories],
        managed_category_names=[c.name for c in current_user.managed_categories],
    )
