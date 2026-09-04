from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    responsible_manager_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    responsible_manager: Mapped["User"] = relationship(
        "User", back_populates="managed_categories"
    )
    claims: Mapped[list["Claim"]] = relationship("Claim", back_populates="category")
