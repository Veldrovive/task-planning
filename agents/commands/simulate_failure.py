from typing import List, TYPE_CHECKING

from .__command import Command
from requirements import AgentRequirementID
from models.commands import SimulateFailureReqData, SimulateFailureResData, FailureType

if TYPE_CHECKING:
    from agents import AgentManager

class SimulateFailureCommand(Command[SimulateFailureReqData, SimulateFailureResData]):
    def __init__(self, agent_manager: 'AgentManager', type: FailureType):
        super().__init__(agent_manager)
        self.type = type

    def format_data(self) -> SimulateFailureReqData:
        return SimulateFailureReqData(failureType=self.type)

    def get_agent_requirements(self) -> List[AgentRequirementID]:
        return []

    def get_fuel_requirement(self) -> int:
        return 0

    def get_time_requirement(self) -> int:
        return 0