from pydantic import BaseModel
from enum import Enum

class FailureType(Enum):
    """
    The set of failure types that the agent should be able to simulate
    """
    CRASH = "crash"
    REBOOT = "reboot"
    COMMAND_FAILED = "commandFailed"

class SimulateFailureReqData(BaseModel):
    failureType: FailureType

class SimulateFailureResData(BaseModel):
    pass
