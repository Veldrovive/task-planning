from .__task import Task
from typing import List, Optional, TYPE_CHECKING

from requirements import AgentRequirementID
from agents.commands import Command, SayCommand, ScanCommand, MoveCommand, GetStateCommand
from models.commands import ScanResData, FaceTo, MoveTo
from models import AgentState, StateLocation
from worlds import SubWorld, PathPlanner
from models.failures import CommandException, FailureID

if TYPE_CHECKING:
    from agents import AgentManager

class SolveMazeTask(Task):
    def __init__(self, agent_manager: 'AgentManager', world: SubWorld, sight_radius: int = 4, goal_block: str = "minecraft:gold_block", scan_every: Optional[int] = None):
        super().__init__(agent_manager)
        self.scan = ScanCommand(self.agent_manager, sight_radius)
        self.move = MoveCommand(self.agent_manager)
        self.commands: List[Command] = [self.scan, self.move]

        self.world = world
        self.path_planner = PathPlanner(world)
        self.goal_block = goal_block
        self.scan_every = scan_every

    def get_agent_requirements(self) -> List[AgentRequirementID]:
        # We have a list of static command for this one so we can use the helper functions to get the requirements
        self.sum_command_agent_requirements(self.commands)

    def get_fuel_requirement(self) -> int:
        # self.sum_command_fuel_requirements(self.commands)
        # Unknown, but large
        return 100

    def get_time_requirement(self) -> int:
        # self.sum_command_time_requirements(self.commands)
        # Unknown, but large
        return 100

    async def run(self) -> None:
        """
        To make a pokehole, we run the move_and_dig command to dig the hole, then the move command to move back to the starting position.
        """
        say_start = SayCommand(self.agent_manager, "Finding Goal...")

        alignment_blocks = ["minecraft:gold_block", "minecraft:iron_block", "minecraft:diamond_block", "minecraft:coal_block"]

        async def scan():
            block_data: ScanResData = await self.scan.run()
            self.world.set_blocks(block_data.blockMap.items())
            # print([pos.__str__() for pos, block in block_data.blockMap.items()])
            for pos, block in block_data.blockMap.items():
                # print(block.name)
                if block.name in alignment_blocks:
                    print(f"Found alignment block {block.name} at {pos}")
            # self.world.show()
            return block_data
        
        block_data = await scan()

        # Find the position of the goal
        goal_positions = []
        for pos, block in block_data.blockMap.items():
            if block.name == self.goal_block:
                goal_positions.append(pos)
        if len(goal_positions) == 0:
            print("Could not find goal block")
            await SayCommand(self.agent_manager, "Could not find goal block").run()
            return

        # goal_state = AgentState(
        #     location = StateLocation(forward=goal_position.forward, side=goal_position.side, up=goal_position.up + 1),
        # )
        goal_states = []
        for goal_position in goal_positions:
            goal_states.append(AgentState(
                location = StateLocation(forward=goal_position.forward, side=goal_position.side, up=goal_position.up + 1),
            ))
        print(f"Goal states: ", goal_states)

        reject_out_of_plane = self.path_planner.reject_out_of_plane_factory(goal_states[0])
        
        while True:
            # Find a path to the target, execute it, if we encounter a MOVEMENT_OBSTRUCTED failure, scan and try again
            start_state: AgentState = await GetStateCommand(self.agent_manager).run()
            print(f"Starting pathfind iteration... \n\tStart: {start_state} \n\tGoals: {goal_states}")
            print(f"\tStart state in world: {self.world.in_world(start_state.location)}, {self.world.get_block(start_state.location)}")
            path = self.path_planner.find_state_path_to_any(start_state, goal_states, assume_occupied=False, reject_neighbors=reject_out_of_plane)
            if path is None:
                print("Could not find path to goal")
                await SayCommand(self.agent_manager, "Could not find path to goal").run()
                return
            print(f"\tPath length: {len(path)}")
            will_complete = True
            if self.scan_every is not None:
                if len(path) > self.scan_every:
                    will_complete = False
                path = path[:self.scan_every]
            move_commands = []
            for state in path:
                move_to = MoveTo(forward=state.location.forward, side=state.location.side, up=state.location.up)
                face_to = FaceTo(forward=state.orientation.forward, side=state.orientation.side, up=state.orientation.up)
                move_commands.append(MoveCommand(self.agent_manager, move_to=move_to, face_to=face_to))
            try:
                await self.agent_manager.send_command_set(move_commands)
                if will_complete:
                    break
                await scan()
            except CommandException as e:
                if e.failure_id == FailureID.MOVEMENT_OBSTRUCTED:
                    await scan()
                    await SayCommand(self.agent_manager, "Movement obstructed... Replanning").run()
                    print("Movement obstructed, rescanning")
                    continue
                else:
                    print(e)
                    raise e
        
        await SayCommand(self.agent_manager, "Goal Reached").run()
        self.world.show()
