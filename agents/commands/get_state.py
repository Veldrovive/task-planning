from typing import List, TYPE_CHECKING

from .__command import Command
from requirements import AgentRequirementID
from models.commands import GetStateReqData, GetStateResData

if TYPE_CHECKING:
    from agents import AgentManager

class GetStateCommand(Command[GetStateReqData, GetStateResData]):
    def __init__(
        self, agent_manager: 'AgentManager',
    ):
        super().__init__(agent_manager)

    def format_data(self) -> GetStateReqData:
        return GetStateReqData()

    def get_agent_requirements(self) -> List[AgentRequirementID]:
        return []

    def get_fuel_requirement(self) -> int:
        return 0

    def get_time_requirement(self) -> int:
        return 0