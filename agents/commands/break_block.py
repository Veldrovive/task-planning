from typing import List, TYPE_CHECKING

from .__command import Command
from requirements import AgentRequirementID
from models.commands import BreakBlockReqData, BreakBlockResData, Direction

if TYPE_CHECKING:
    from agents import AgentManager

class BreakBlockCommand(Command[BreakBlockReqData, BreakBlockResData]):
    def __init__(self, agent_manager: 'AgentManager', direction: Direction, require_inventory_space: bool = False):
        super().__init__(agent_manager)
        self.direction = direction
        self.require_inventory_space = require_inventory_space

    def format_data(self) -> BreakBlockReqData:
        return BreakBlockReqData(direction=self.direction, requireInventorySpace=self.require_inventory_space)

    def get_agent_requirements(self) -> List[AgentRequirementID]:
        return [AgentRequirementID.CAN_BREAK]

    def get_fuel_requirement(self) -> int:
        return 0

    def get_time_requirement(self) -> int:
        return 0