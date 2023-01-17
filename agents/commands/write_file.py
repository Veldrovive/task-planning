from typing import List, TYPE_CHECKING

from .__command import Command
from requirements import AgentRequirementID
from models.commands import WriteFileReqData, WriteFileResData

if TYPE_CHECKING:
    from agents import AgentManager

class WriteFileCommand(Command[WriteFileReqData, WriteFileResData]):
    def __init__(
        self, agent_manager: 'AgentManager',
        filepath: str,
        content: str,
    ):
        super().__init__(agent_manager)
        self.filepath = filepath
        self.content = content

    def format_data(self) -> WriteFileReqData:
        return WriteFileReqData(filepath=self.filepath, content=self.content)

    def get_agent_requirements(self) -> List[AgentRequirementID]:
        return [AgentRequirementID.CAN_SCAN]

    def get_fuel_requirement(self) -> int:
        return 0

    def get_time_requirement(self) -> int:
        return 0