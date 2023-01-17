from typing import TYPE_CHECKING

from .__command import Command
from models.commands import InitializeReqData, InitializeResData, FieldID, FieldRequirement

if TYPE_CHECKING:
    from agents import AgentManager

class InitializeCommand(Command[InitializeReqData, InitializeResData]):
    def __init__(self, agent_manager: 'AgentManager'):
        super().__init__(agent_manager)

    def format_data(self) -> InitializeReqData:
        return InitializeReqData(
            requiredFields=[
                FieldRequirement(fieldId=FieldID.ID, fieldName="ID", fieldDescription="The ID of the agent"),
                FieldRequirement(fieldId=FieldID.LABEL, fieldName="Label", fieldDescription="The label of the agent")
            ]
        )

    def get_agent_requirements(self):
        return []

    def get_fuel_requirement(self):
        return 0

    def get_time_requirement(self):
        return 0
