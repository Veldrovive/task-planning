from typing import List, Optional, TYPE_CHECKING

from .__command import Command
from requirements import AgentRequirementID
from models.commands import ScanReqData, ScanResData

if TYPE_CHECKING:
    from agents import AgentManager

class ScanCommand(Command[ScanReqData, ScanResData]):
    def __init__(
        self, agent_manager: 'AgentManager',
        radius: int = 8,
    ):
        super().__init__(agent_manager)
        self.radius = radius

    def format_data(self) -> ScanReqData:
        return ScanReqData(radius=self.radius)

    def get_agent_requirements(self) -> List[AgentRequirementID]:
        return [AgentRequirementID.CAN_SCAN]

    def get_fuel_requirement(self) -> int:
        # TODO: Calculate fuel requirement
        return 0

    def get_time_requirement(self) -> int:
        return 1