"""
This task uses a scanner to plan a route to the closest of a set of locations without needing prior knowledge of the world.
"""

from .__task import Task
from typing import List, Optional, Union, TYPE_CHECKING

from requirements import AgentRequirementID
from agents.commands import Command, SayCommand, ScanCommand, MoveCommand, GetStateCommand
from models.commands import ScanResData, FaceTo, MoveTo
from models import AgentState, StateLocation
from worlds import SubWorld, PathPlanner
from models.failures import CommandException, FailureID

if TYPE_CHECKING:
    from agents import AgentManager

class ScanAndPathfindTask(Task):
    def __init__(self, agent_manager: 'AgentManager', world: SubWorld, goal: Union[List[AgentState], AgentState], sight_radius: int = 4):
        super().__init__(agent_manager)
        self.scan = ScanCommand(self.agent_manager, sight_radius)
        self.move = MoveCommand(self.agent_manager)
        self.commands: List[Command] = [self.scan, self.move]

        self.world = world
        self.path_planner = PathPlanner(world)
        if isinstance(goal, list):
            self.goal_states = goal
        else:
            self.goal_states = [goal]

    def get_agent_requirements(self) -> List[AgentRequirementID]:
        self.sum_command_agent_requirements(self.commands)

    def get_fuel_requirement(self) -> int:
        return 100

    def get_time_requirement(self) -> int:
        return 100

    async def run(self) -> None:
        async def scan():
            block_data: ScanResData = await self.scan.run()
            self.world.set_blocks(block_data.blockMap.items())
            # self.world.show()
            return block_data

        await scan()
        while True:
            start_state: AgentState = await GetStateCommand(self.agent_manager).run()
            path = self.path_planner.find_state_path_to_any(start_state, self.goal_states, assume_occupied=False)
            if path is None:
                return False, "No path found"
            
            move_commands = []
            for state in path:
                move_to = MoveTo(forward=state.location.forward, side=state.location.side, up=state.location.up)
                face_to = FaceTo(forward=state.orientation.forward, side=state.orientation.side, up=state.orientation.up)
                move_commands.append(MoveCommand(self.agent_manager, move_to=move_to, face_to=face_to))

            try:
                await self.agent_manager.send_command_set(move_commands)
                return True, None
            except CommandException as e:
                if e.failure_id == FailureID.MOVEMENT_OBSTRUCTED:
                    await scan()
                    continue
                else:
                    print(e)
                    return False, e