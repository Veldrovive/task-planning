"""
Holds the string IDs for all commands.
"""

from enum import Enum

class CommandID(Enum):
    """
    Holds the string IDs for all commands.
    """
    INITIALIZE = "initialize"
    PING = "ping"
    SCAN = "scan"
    CLEAR_TERMINAL = "clearTerminal"
    SAY = "say"
    SIMULATE_FAILURE = "simulateFailure"
    WRITE_FILE = "writeFile"
    MOVE = "move"
    FACE = "face"
    MOVE_AND_DIG = "moveAndDig"
    CHOP_VERTICAL_TREE = "chopVerticalTree"
    CHOP_FOUR_TREE = "chopFourTree"
    PLACE = "place"
    DROP = "drop"
    BREAK_BLOCK = "breakBlock"
    GET_INVENTORY = "getInventory"
    GET_STATE = "getState"

class Direction(Enum):
    """
    The set of directions that the agent can move
    """
    UP = "up"
    DOWN = "down"
    FRONT = "front"