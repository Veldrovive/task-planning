from .__task import Task
from typing import List, Dict, TYPE_CHECKING

from requirements import AgentRequirementID
from agents.commands import Command, MoveAndDigCommand, MoveCommand, SayCommand, GetInventoryCommand, PlaceCommand, BreakBlockCommand, DropCommand
from models.commands import MoveTo, FaceTo, Direction, GetInventoryResData, BlockAmount
from models.failures import CommandException, FailureID

from push_notification import notify

if TYPE_CHECKING:
    from agents import AgentManager

class PokeHoleTaskV2(Task):
    def __init__(self, agent_manager: 'AgentManager', num_blocks: int, place_torches_every: int = 14, notify: bool = False):
        super().__init__(agent_manager)
        self.num_blocks = num_blocks
        self.notify = notify
        self.commands: Dict[str, List[Command]] = {
            "get_inventory": [GetInventoryCommand(agent_manager), GetInventoryCommand(agent_manager)],
            "poke_hole": [MoveAndDigCommand(agent_manager, num_blocks, placeTorchesEvery=place_torches_every)],
            "return": [MoveCommand(agent_manager, face_to=FaceTo(forward=-1, side=0, up=0)), MoveAndDigCommand(agent_manager, num_blocks, breakAbove=False, placeTorchesEvery=None), MoveCommand(agent_manager, face_to=FaceTo(forward=1, side=0, up=0))],
            "place_chest": [BreakBlockCommand(agent_manager, direction=Direction.DOWN, require_inventory_space=False), PlaceCommand(agent_manager, direction=Direction.DOWN, block="minecraft:chest")],
            "deposit": [DropCommand(agent_manager, direction=Direction.DOWN)],
            "finish": [SayCommand(agent_manager, f"Made a hole {num_blocks} blocks deep!")]
        }

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
        # Initialize: get if we have a chest to place and select the chest we will use
        initial_inventory: GetInventoryResData = await self.commands["get_inventory"][0].run()
        # We need to know which block we can use as a chest
        chest_blocks = [name for name in initial_inventory.inventory.blockCounts.keys() if "chest" in name]
        has_chest = len(chest_blocks) > 0
        if not has_chest:
            print("Skipping chest as none are available")
            await SayCommand(self.agent_manager, "Skipping chest as none are available").run()
        else:
            # We want to use the chest with the least number of them left
            chest_blocks.sort(key=lambda name: initial_inventory.inventory.blockCounts[name])
            print(f"Using {chest_blocks[0]} as chest")
            await SayCommand(self.agent_manager, f"Using {chest_blocks[0]} as chest").run()
            self.commands["place_chest"][1].block = chest_blocks[0]

        # Run the main bulk of the pokehole where we mine and then return
        await self.commands["poke_hole"][0].run(ignore_failure=[FailureID.CANNOT_BREAK_UNBREAKABLE_BLOCK])
        await self.agent_manager.send_command_set(self.commands["return"], ignore_failure=[FailureID.CANNOT_BREAK_UNBREAKABLE_BLOCK])

        # Now we want to get the extra blocks we got from the pokehole and place them into a chest
        if has_chest:
            await self.agent_manager.send_command(self.commands["place_chest"][0], ignore_failure=[FailureID.NO_BLOCK_TO_DIG, FailureID.CANNOT_BREAK_UNBREAKABLE_BLOCK])
        final_inventory: GetInventoryResData = await self.commands["get_inventory"][1].run()
        if has_chest:
            await self.agent_manager.send_command(self.commands["place_chest"][1], ignore_failure=[FailureID.NO_BLOCK_AVAILABLE])
        to_drop: List[BlockAmount] = []  # Will hold the extra blocks we got from this task
        for block, quantity in final_inventory.inventory.blockCounts.items():
            diff = 0
            if block in initial_inventory.inventory.blockCounts:
                diff = quantity - initial_inventory.inventory.blockCounts[block]
            else:
                diff = quantity
            if diff > 0:
                to_drop.append(BlockAmount(block=block, amount=diff))
        if len(to_drop) > 0:
            self.commands["deposit"][0].blocks = to_drop
            await self.commands["deposit"][0].run()
        extra_items_string = "Mined:\n"
        for block_data in to_drop:
            block, quantity = block_data.block, block_data.amount
            extra_items_string += f"\t{block}: {quantity}\n"
        await SayCommand(self.agent_manager, extra_items_string).run()
        await self.commands["finish"][0].run()

        if self.notify:
            notify("Pokehole returned for: ", self.agent_manager.label)
