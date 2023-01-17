from typing import List, TYPE_CHECKING

from .__command import Command
from requirements import AgentRequirementID
from models.commands import SayReqData, SayResData

if TYPE_CHECKING:
    from agents import AgentManager

class SayCommand(Command[SayReqData, SayResData]):
    def __init__(self, agent_manager: 'AgentManager', message: str, wait: int = 0):
        super().__init__(agent_manager)
        self.message = message
        self.wait = wait

    def format_data(self) -> SayReqData:
        return SayReqData(message=self.message, wait=self.wait)

    def get_agent_requirements(self) -> List[AgentRequirementID]:
        return []

    def get_fuel_requirement(self) -> int:
        return 0

    def get_time_requirement(self) -> int:
        return 0