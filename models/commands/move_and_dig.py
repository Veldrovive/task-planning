from pydantic import BaseModel
from typing import Optional

class MoveAndDigReqData(BaseModel):
    numBlocks: int
    breakAbove: bool = True
    placeTorchesEvery: Optional[int] = 14

class MoveAndDigResData(BaseModel):
    pass