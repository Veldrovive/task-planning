from typing import List, TYPE_CHECKING

from .__command import Command
from requirements import AgentRequirementID
from models.commands import MoveAndDigReqData, MoveAndDigResData

if TYPE_CHECKING:
    from agents import AgentManager

class MoveAndDigCommand(Command[MoveAndDigReqData, MoveAndDigResData]):
    def __init__(self, agent_manager: 'AgentManager', num_blocks: int, breakAbove: bool = True, placeTorchesEvery: int = 14):
        super().__init__(agent_manager)
        self.num_blocks = num_blocks
        self.breakAbove = breakAbove
        self.placeTorchesEvery = placeTorchesEvery

    def format_data(self) -> MoveAndDigReqData:
        return MoveAndDigReqData(numBlocks=self.num_blocks, breakAbove=self.breakAbove, placeTorchesEvery=self.placeTorchesEvery)

    def get_agent_requirements(self) -> List[AgentRequirementID]:
        return [AgentRequirementID.CAN_BREAK, AgentRequirementID.CAN_MOVE, AgentRequirementID.CAN_PLACE]

    def get_fuel_requirement(self) -> int:
        return self.num_blocks

    def get_time_requirement(self) -> int:
        return self.num_blocks * 2