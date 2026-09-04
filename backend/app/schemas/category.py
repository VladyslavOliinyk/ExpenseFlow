from pydantic import BaseModel


class CategoryOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    responsible_manager_id: int
