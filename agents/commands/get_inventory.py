from typing import List, TYPE_CHECKING

from .__command import Command
from requirements import AgentRequirementID
from models.commands import GetInventoryReqData, GetInventoryResData

if TYPE_CHECKING:
    from agents import AgentManager

class GetInventoryCommand(Command[GetInventoryReqData, GetInventoryResData]):
    def __init__(self, agent_manager: 'AgentManager'):
        super().__init__(agent_manager)

    def format_data(self) -> GetInventoryReqData:
        return GetInventoryReqData()

    def get_agent_requirements(self) -> List[AgentRequirementID]:
        return [AgentRequirementID.HAS_INVENTORY]

    def get_fuel_requirement(self) -> int:
        return 0

    def get_time_requirement(self) -> int:
        return 0