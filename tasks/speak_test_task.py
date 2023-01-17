from .__task import Task
from typing import List, TYPE_CHECKING

from requirements import AgentRequirementID
from agents.commands import Command, SayCommand, SimulateFailureCommand
from models.commands import SayResData, FailureType
from models.failures import CommandException, FailureID

if TYPE_CHECKING:
    from agents import AgentManager

class SpeakTestTask(Task):
    def __init__(self, agent_manager: 'AgentManager'):
        super().__init__(agent_manager)

    def get_agent_requirements(self) -> List[AgentRequirementID]:
        # We have a list of static command for this one so we can use the helper functions to get the requirements
        self.sum_command_agent_requirements(self.commands)

    def get_fuel_requirement(self) -> int:
        self.sum_command_fuel_requirements(self.commands)

    def get_time_requirement(self) -> int:
        self.sum_command_time_requirements(self.commands)

    async def run(self) -> None:
        """
        To make a pokehole, we run the move_and_dig command to dig the hole, then the move command to move back to the starting position.
        """
        sayInit = SayCommand(self.agent_manager, "Starting test task...")
        sayInitRes: SayResData = await self.agent_manager.send_command(sayInit)
        say2 = SayCommand(self.agent_manager, f'In initial run, I said: "{sayInitRes.said}"')
        await self.agent_manager.send_command(say2)
        try:
            await self.agent_manager.send_command(SimulateFailureCommand(self.agent_manager, FailureType.COMMAND_FAILED))
        except CommandException as e:
            if e.failure_id == FailureID.SIMULATED_FAILURE:
                print("Simulated failure worked!")
            else:
                raise e
        say3 = SayCommand(self.agent_manager, f'Saying and waiting for 2 seconds', wait=2)
        say4 = SayCommand(self.agent_manager, f'Done!')
        await self.agent_manager.send_command_set([say3, say4])
