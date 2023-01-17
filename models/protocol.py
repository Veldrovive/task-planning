from pydantic import BaseModel, Field, validator
from typing import Any, Generic, TypeVar, Optional, List
from uuid import uuid4
from enum import Enum
from .commands import CommandID
from models.failures import Failure
from models.commands import command_res_class_map

class TopicMessage(BaseModel):
    topic: str = Field(default_factory=uuid4)
    message: Any

CommandTypeReqData = TypeVar("CommandTypeReqData", bound=BaseModel)
class CommandReq(BaseModel, Generic[CommandTypeReqData]):
    command: CommandID
    data: Optional[CommandTypeReqData]

CommandTypeResData = TypeVar("CommandTypeResData", bound=BaseModel)
class CommandRes(BaseModel, Generic[CommandTypeResData]):
    command: CommandID
    data: Optional[CommandTypeResData]
    startTime: int
    endTime: int

class SetStatus(Enum):
    COMPLETED = "completed"
    FAILED = "failed"

class SetResponse(BaseModel):
    commands: List[CommandRes]
    setStatus: SetStatus
    failure: Optional[Failure]

    # Commands can be parsed to their correct type by inspecting the command ID and using the command_res_class_map
    @validator("commands", pre=True)
    def parse_commands(cls, commands):
        for command in commands:
            if "data" in command and command["data"] is not None:
                command_id = command["command"]
                CommandResClass = command_res_class_map[command_id]
                command["data"] = CommandResClass.parse_obj(command["data"])
        return commands
    

class CommandSet(BaseModel):
    commands: List[CommandReq]

class CommandSetResponseMessage(TopicMessage):
    message: SetResponse