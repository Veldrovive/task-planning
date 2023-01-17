from .__task import Task
from typing import List, TYPE_CHECKING

from requirements import AgentRequirementID
from agents.commands import Command, SayCommand, ScanCommand, MoveCommand
from models.commands import ScanResData, FaceTo, MoveTo
# from models.failures import CommandException, FailureID

if TYPE_CHECKING:
    from agents import AgentManager

class ScanTestTask(Task):
    def __init__(self, agent_manager: 'AgentManager', radius: int = 8):
        super().__init__(agent_manager)
        self.scan = ScanCommand(self.agent_manager, radius)
        self.commands: List[Command] = [self.scan]

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
        say_start = SayCommand(self.agent_manager, "Starting scan...")
        say_end = SayCommand(self.agent_manager, f'Scan Complete')

        async def scan_stone():
            block_data: ScanResData = (await self.agent_manager.send_command_set([say_start, self.scan, say_end]))[1]
            # Find the position of the minecraft:stone
            for pos, block in block_data.blockMap.items():
                # print(pos, block.name)
                if block.name == "minecraft:stone":
                    print("Found stone at", pos)
                    return pos

        stone_1 = await scan_stone()

        # Turn to face the side
        await MoveCommand(self.agent_manager, face_to = FaceTo(side=1), move_to=MoveTo(side=1)).run()
        stone_2 = await scan_stone()

        # Move up
        await MoveCommand(self.agent_manager, move_to=MoveTo(up=1, side=1)).run()
        stone_3 = await scan_stone()

        # Move to the other side of the block
        await MoveCommand(self.agent_manager, move_to=MoveTo(forward=2, up=1)).run()
        stone_4 = await scan_stone()

        # Move to the final side of the block
        await MoveCommand(self.agent_manager, move_to=MoveTo(side=-1, up=1)).run()
        stone_5 = await scan_stone()
        
        await MoveCommand(self.agent_manager, face_to = FaceTo(forward=1), move_to=MoveTo(forward=0)).run()
        # It should be in the same position both times because this reference frame is fixed relative to the world and not fixed relative to the turtle
        # In reality, the mod actually uses a world fixed reference frame so it actually turns relative to the robot and this all gets messed up but hopefully the mod author will hear my plea and change that behavior
