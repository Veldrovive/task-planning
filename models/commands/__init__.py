from .__command_enums import CommandID

from .chop_four_tree import *
from .chop_vertical_tree import *
from .clear_terminal import *
from .drop import *
from .initialize import *
from .move_and_dig import *
from .move import *
from .place import *
from .say import *
from .scan import *
from .simulate_failure import *
from .write_file import *
from .break_block import *
from .get_inventory import *
from .drop import *
from .get_state import *

from typing import Dict
command_res_class_map: Dict[CommandID, BaseModel] = {
    CommandID.CHOP_FOUR_TREE.value: ChopFourTreeResData,
    CommandID.CHOP_VERTICAL_TREE.value: ChopVerticalTreeResData,
    CommandID.CLEAR_TERMINAL.value: ClearTerminalResData,
    CommandID.DROP.value: DropResData,
    CommandID.INITIALIZE.value: InitializeResData,
    CommandID.MOVE_AND_DIG.value: MoveAndDigResData,
    CommandID.MOVE.value: MoveResData,
    CommandID.PLACE.value: PlaceResData,
    CommandID.SAY.value: SayResData,
    CommandID.SCAN.value: ScanResData,
    CommandID.SIMULATE_FAILURE.value: SimulateFailureResData,
    CommandID.WRITE_FILE.value: WriteFileResData,
    CommandID.BREAK_BLOCK.value: BreakBlockResData,
    CommandID.GET_INVENTORY.value: GetInventoryResData,
    CommandID.DROP.value: DropResData,
    CommandID.GET_STATE.value: GetStateResData,
}