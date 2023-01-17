from pydantic import BaseModel
from enum import Enum
from typing import Optional

class FailureID(Enum):
    """
    Enumerates the types of failures we expect to encounter
    """
    ALREADY_COMPLETE = "Already complete"
    NOT_IMPLEMENTED = "Not implemented"
    SIMULATED_FAILURE = "Simulated failure"
    CANNOT_BREAK_UNBREAKABLE_BLOCK = "Cannot break unbreakable block"
    NO_BLOCK_AVAILABLE = "No block available"
    NO_BLOCK_TO_DIG = "Nothing to dig here"
    NOT_ENOUGH_INVENTORY_SPACE = "Not enough inventory space"
    COMMAND_REQUIREMENTS_NOT_MET = "Command requirements not met"
    PERIPHERAL_NOT_FOUND = "Peripheral not found"
    MOVEMENT_OBSTRUCTED = "Movement obstructed"
    OUT_OF_FUEL = "Out of fuel"
    SCAN_ON_COOLDOWN = "scanBlocks is on cooldown"


class Failure(BaseModel):
    """
    Base class for failures
    """
    failureID: FailureID
    message: Optional[str]