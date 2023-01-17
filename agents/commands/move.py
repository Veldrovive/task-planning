from typing import List, Optional, TYPE_CHECKING

from .__command import Command
from requirements import AgentRequirementID
from models.commands import MoveReqData, MoveResData, MoveTo, MoveBy, FaceTo

if TYPE_CHECKING:
    from agents import AgentManager

class MoveCommand(Command[MoveReqData, MoveResData]):
    def __init__(self, agent_manager: 'AgentManager', move_to: Optional[MoveTo] = None, move_by: Optional[MoveBy] = None, face_to: Optional[FaceTo] = None):
        super().__init__(agent_manager)
        self.move_to = move_to
        self.move_by = move_by
        self.face_to = face_to

    def format_data(self) -> MoveReqData:
        return MoveReqData(moveTo=self.move_to, moveBy=self.move_by, faceTo=self.face_to)

    def get_agent_requirements(self) -> List[AgentRequirementID]:
        return [AgentRequirementID.CAN_MOVE]

    def get_fuel_requirement(self) -> int:
        return self.num_blocks

    def get_time_requirement(self) -> int:
        return self.num_blocks