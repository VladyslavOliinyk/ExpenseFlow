from pydantic import BaseModel


class UserOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    email: str
    managed_category_ids: list[int] = []
    managed_category_names: list[str] = []
