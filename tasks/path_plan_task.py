from .__task import Task
from typing import List, TYPE_CHECKING

from requirements import AgentRequirementID
from agents.commands import Command, MoveCommand, SayCommand, GetStateCommand
from models import AgentState
from models.commands import FaceTo, MoveTo
from worlds import SubWorld, PathPlanner
# from models.failures import CommandException, FailureID

if TYPE_CHECKING:
    from agents import AgentManager

class PathPlanTask(Task):
    def __init__(self, agent_manager: 'AgentManager', world: SubWorld, goal_state: AgentState):
        super().__init__(agent_manager)
        self.world = world
        self.planner = PathPlanner(world)
        self.goal_state = goal_state

        self.move = MoveCommand(self.agent_manager)
        self.commands: List[Command] = [self.move]

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
        say_start = SayCommand(self.agent_manager, "Starting planning...")
        start_state: AgentState = (await self.agent_manager.send_command_set([say_start, GetStateCommand(self.agent_manager)]))[1]
        print("Start state:", start_state)

        path = self.planner.find_state_path(start_state, self.goal_state)

        move_commands = []
        for state in path:
            move_to = MoveTo(forward=state.location.forward, side=state.location.side, up=state.location.up)
            face_to = FaceTo(forward=state.orientation.forward, side=state.orientation.side, up=state.orientation.up)
            move_commands.append(MoveCommand(self.agent_manager, move_to=move_to, face_to=face_to))

        say_end = SayCommand(self.agent_manager, "Done planning!")

        await self.agent_manager.send_command_set([*move_commands, say_end])

        await SayCommand(self.agent_manager, "Finished").run()

        # block_data: ScanResData = (await self.agent_manager.send_command_set([say_start, self.scan, say_end]))[1]
        # # Find the position of the minecraft:stone
        # for pos, block in block_data.blockMap.items():
        #     if block.name == "minecraft:stone":
        #         print("Found stone at", pos)
        #         break

        # # Turn to face the side
        # await MoveCommand(self.agent_manager, face_to = FaceTo(side=1)).run()
        # block_data_2: ScanResData = (await self.agent_manager.send_command_set([say_start, self.scan, say_end]))[1]
        # await MoveCommand(self.agent_manager, face_to = FaceTo(forward=1)).run()

        # # Find the position of the minecraft:stone
        # for pos, block in block_data_2.blockMap.items():
        #     if block.name == "minecraft:stone":
        #         print("Found stone at", pos)
        #         break

        # It should be in the same position both times because this reference frame is fixed relative to the world and not fixed relative to the turtle
        # In reality, the mod actually uses a world fixed reference frame so it actually turns relative to the robot and this all gets messed up but hopefully the mod author will hear my plea and change that behavior
