from pydantic import BaseModel, root_validator
from typing import Dict, List, Tuple
from models.__agent_models import StateLocation
from models.__world_models import BlockData, LuaList

class ScanReqData(BaseModel):
    radius: int

class ScanResData(BaseModel):
    blocks: LuaList[Tuple[int, int, int, str]]
    blockMap: Dict[StateLocation, BlockData]

    @root_validator(pre=True)
    def reformat(cls, values):
        # We actually get the data as an array [ [forward, side, up, blockName], ... ] and we need to convert it to a dictionary
        blockMap = {}
        for forward, side, up, name in values['blocks']:
            # print(f"Reformatting {forward}, {side}, {up}, {name}")
            position = StateLocation(side=side, up=up, forward=forward)
            blockMap[position] = BlockData(name=name)
        values['blockMap'] = blockMap
        return values