from pydantic import BaseModel
from typing import Literal

class Item(BaseModel):
    start: str
    destination: str
    age: int
    gender: Literal['男', '女']
