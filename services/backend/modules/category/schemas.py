from typing import Union

from pydantic import BaseModel, ConfigDict


class CategoryFull(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    parent_id: Union[int, None]
    name: str
