from pydantic import BaseModel
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, TYPE_CHECKING, Union
from models.failures import FailureID

if TYPE_CHECKING:
    from agents import AgentManager

CommandTypeReqData = TypeVar("CommandTypeReqData", bound=BaseModel)
CommandTypeResData = TypeVar("CommandTypeResData", bound=BaseModel)
class Command(ABC, Generic[CommandTypeReqData, CommandTypeResData]):
    def __init__(self, agent_manager: 'AgentManager'):
        self.agent_manager = agent_manager

    @abstractmethod
    def format_data(self) -> CommandTypeReqData:
        pass

    async def run(self, ignore_failure: Union[bool, List[FailureID]] = False):
        """
        Small wrapper around the agent manager command to make sending easier
        """
        return await self.agent_manager.send_command(self, ignore_failure=ignore_failure)

    @abstractmethod
    def get_agent_requirements(self) -> List[str]:
        pass

    @abstractmethod
    def get_fuel_requirement(self) -> int:
        pass

    @abstractmethod
    def get_time_requirement(self) -> int:
        pass
