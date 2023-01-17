from pydantic import BaseModel, root_validator
from typing import List
from models.commands.__command_enums import Direction

class BlockAmount(BaseModel):
    block: str
    amount: int

class DropReqData(BaseModel):
    direction: Direction = Direction.FRONT,
    allOf: List[str] = None
    allBut: List[str] = None
    blocks: List[BlockAmount] = None

    # Only one of these can be set at a time
    @root_validator
    def check_drop_req_data(cls, values):
        allOf = values.get("allOf")
        allBut = values.get("allBut")
        blocks = values.get("blocks")
        if allOf is None and allBut is None and blocks is None:
            raise ValueError("One of allOf, allBut, or blocks must be specified")
        num_set = sum([1 if x is not None else 0 for x in [allOf, allBut, blocks]])
        if num_set > 1:
            raise ValueError("Only one of allOf, allBut, or blocks can be specified")
        return values

class DropResData(BaseModel):
    pass