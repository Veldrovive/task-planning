from pydantic import BaseModel
from .__command_enums import Direction

class PlaceReqData(BaseModel):
    block: str
    direction: Direction

class PlaceResData(BaseModel):
    pass