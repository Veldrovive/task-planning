from typing import List, Optional, TYPE_CHECKING

from .__command import Command
from requirements import AgentRequirementID
from models.commands import DropReqData, DropResData, BlockAmount, Direction

if TYPE_CHECKING:
    from agents import AgentManager

class DropCommand(Command[DropReqData, DropResData]):
    def __init__(
        self, agent_manager: 'AgentManager',
        direction: Direction = Direction.FRONT,
        all_of: Optional[List[str]] = None,
        all_but: Optional[List[str]] = None,
        blocks: Optional[List[BlockAmount]] = None
    ):
        super().__init__(agent_manager)
        self.direction = direction
        self.all_of = all_of
        self.all_but = all_but
        self.blocks = blocks

    def format_data(self) -> DropReqData:
        return DropReqData(direction=self.direction, allOf=self.all_of, allBut=self.all_but, blocks=self.blocks)

    def get_agent_requirements(self) -> List[AgentRequirementID]:
        return [AgentRequirementID.HAS_INVENTORY]

    def get_fuel_requirement(self) -> int:
        return 0

    def get_time_requirement(self) -> int:
        return 2