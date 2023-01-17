from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING, Union, Dict, Any

from requirements import AgentRequirementID
from agents.commands import Command

if TYPE_CHECKING:
    from agents import AgentManager

CommandSet = Union[List[Command], Dict[Any, List[Command]]]

class Task(ABC):
    def __init__(self, agent_manager: 'AgentManager'):
        self.agent_manager = agent_manager

    def _command_set_to_command_list(self, commands: CommandSet):
        if isinstance(commands, list):
            return commands
        elif isinstance(commands, dict):
            return [command for command_list in commands.values() for command in command_list]
        else:
            raise TypeError(f'Expected a list or dict, got {type(commands)}')

    def sum_command_agent_requirements(self, commands: CommandSet):
        commands = self._command_set_to_command_list(commands)
        requirements = set()
        for command in commands:
            requirements.update(command.get_agent_requirements())
        return list(requirements)
    
    @abstractmethod
    def get_agent_requirements(self) -> List[AgentRequirementID]:
        pass

    def sum_command_fuel_requirements(self, commands: CommandSet):
        commands = self._command_set_to_command_list(commands)
        return sum((command.get_fuel_requirement() for command in commands))

    @abstractmethod
    def get_fuel_requirement(self) -> int:
        pass

    def sum_command_time_requirements(self, commands: CommandSet):
        commands = self._command_set_to_command_list(commands)
        return sum((command.get_time_requirement() for command in commands))

    @abstractmethod
    def get_time_requirement(self) -> int:
        pass

    @abstractmethod
    async def run(self) -> None:
        pass