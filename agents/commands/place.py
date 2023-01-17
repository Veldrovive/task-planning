from typing import List, Optional, TYPE_CHECKING

from .__command import Command
from requirements import AgentRequirementID
from models.commands import PlaceReqData, PlaceResData, Direction

if TYPE_CHECKING:
    from agents import AgentManager

class PlaceCommand(Command[PlaceReqData, PlaceResData]):
    def __init__(self, agent_manager: 'AgentManager', block: str, direction: Direction):
        super().__init__(agent_manager)
        self.block = block
        self.direction = direction

    def format_data(self) -> PlaceReqData:
        return PlaceReqData(block=self.block, direction=self.direction)

    def get_agent_requirements(self) -> List[AgentRequirementID]:
        return [AgentRequirementID.CAN_PLACE]

    def get_fuel_requirement(self) -> int:
        return self.num_blocks

    def get_time_requirement(self) -> int:
        return self.num_blocks