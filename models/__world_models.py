from pydantic import BaseModel, root_validator, parse_obj_as
from typing import Dict, List, Any, Generic, Optional, TypeVar, Union

T = TypeVar('T')
class LuaList(List[T], Generic[T]):
    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, list):
            return v
        elif isinstance(v, dict):
            if len(v) == 0:
                return []
            raise TypeError(f'LuaList must be a list or a dictionary with length 0, not {type(v)}')
        else:
            raise TypeError(f'LuaList must be a list or a dictionary, not {type(v)}')

class BlockData(BaseModel):
    name: str
    occupied: bool
    tags: Optional[Dict[str, bool]]
    state: Any

    @root_validator(pre=True)
    def check_occupied(cls, values):
        values['occupied'] = values['name'] != 'minecraft:air'
        return values

class InventoryData(BaseModel):
    blockNames: LuaList[Union[str, None]]  # An array of block names in the inventory
    blockCounts: Dict[str, int]  # A dictionary of block names to the number of blocks of that type in the inventory
    blockOpenCounts: Dict[str, int]  # A dictionary of block names to the number of blocks of this type that could be inserted into the inventory
    blockSlotMap: Dict[str, LuaList[int]]  # A map from block names to the list of slots that contain blocks of that type
    totallyOpenSlots: int  # The number of slots that are totally open