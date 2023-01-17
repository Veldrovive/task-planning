from typing import List, TYPE_CHECKING

from .__command import Command
from requirements import AgentRequirementID
from models.commands import ChopVerticalTreeReqData, ChopVerticalTreeResData

if TYPE_CHECKING:
    from agents import AgentManager

MAX_TREE_HEIGHT = 16

class ChopVerticalTreeCommand(Command[ChopVerticalTreeReqData, ChopVerticalTreeResData]):
    def __init__(self, agent_manager: 'AgentManager', replace_sapling: bool = True):
        super().__init__(agent_manager)
        self.replace_sapling = replace_sapling

    def format_data(self) -> ChopVerticalTreeReqData:
        return ChopVerticalTreeReqData(replaceSapling=self.replace_sapling)

    def get_agent_requirements(self) -> List[AgentRequirementID]:
        return [AgentRequirementID.CAN_BREAK, AgentRequirementID.CAN_PLACE, AgentRequirementID.CAN_MOVE]

    def get_fuel_requirement(self) -> int:
        return MAX_TREE_HEIGHT * 2 + 1 + 4

    def get_time_requirement(self) -> int:
        return 2 * MAX_TREE_HEIGHT * 2 + 1 + 4