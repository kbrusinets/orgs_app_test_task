from typing import List

from pydantic import BaseModel, ConfigDict

from services.backend.modules.category.schemas import CategoryFull


class OrgFull(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    coordinates: str
    address: str
    categories: List[CategoryFull]
