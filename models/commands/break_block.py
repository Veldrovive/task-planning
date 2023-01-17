from pydantic import BaseModel
from models.commands import Direction
from typing import Optional
from models.__world_models import BlockData

class BreakBlockReqData(BaseModel):
    direction: Optional[Direction] = Direction.FRONT
    requireInventorySpace: Optional[bool] = False    

class BreakBlockResData(BaseModel):
    broke: BlockData