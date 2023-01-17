from pydantic import BaseModel
from models.__world_models import InventoryData

class GetInventoryReqData(BaseModel):
    pass

class GetInventoryResData(BaseModel):
    inventory: InventoryData