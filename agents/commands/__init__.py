from .__command import Command

from .initialize import InitializeCommand
from .move import MoveCommand
from .move_and_dig import MoveAndDigCommand
from .say import SayCommand
from .simulate_failure import SimulateFailureCommand
from .place import PlaceCommand
from .break_block import BreakBlockCommand
from .get_inventory import GetInventoryCommand
from .chop_four_tree import ChopFourTreeCommand
from .chop_vertical_tree import ChopVerticalTreeCommand
from .clear_terminal import ClearTerminalCommand
from .drop import DropCommand
from .scan import ScanCommand
from .write_file import WriteFileCommand
from .get_state import GetStateCommand

from models.commands import CommandID
command_class_map = {
    InitializeCommand: CommandID.INITIALIZE,
    MoveCommand: CommandID.MOVE,
    MoveAndDigCommand: CommandID.MOVE_AND_DIG,
    SayCommand: CommandID.SAY,
    SimulateFailureCommand: CommandID.SIMULATE_FAILURE,
    PlaceCommand: CommandID.PLACE,
    BreakBlockCommand: CommandID.BREAK_BLOCK,
    GetInventoryCommand: CommandID.GET_INVENTORY,
    ChopFourTreeCommand: CommandID.CHOP_FOUR_TREE,
    ChopVerticalTreeCommand: CommandID.CHOP_VERTICAL_TREE,
    ClearTerminalCommand: CommandID.CLEAR_TERMINAL,
    DropCommand: CommandID.DROP,
    ScanCommand: CommandID.SCAN,
    WriteFileCommand: CommandID.WRITE_FILE,
    GetStateCommand: CommandID.GET_STATE,
}