from dataclasses import dataclass
from pydantic import BaseModel, Field
from typing import Any, Callable, Optional, List, Dict, Tuple, TYPE_CHECKING

from queue import PriorityQueue
from models.__world_models import BlockData
from models.__agent_models import AgentState, StateLocation

if TYPE_CHECKING:
    from agents import AgentManager

# class Position(BaseModel):
#     """
#     A position is a location in the world.
#     It is defined by a SubWorld and a relative position within that SubWorld.
#     """
#     x: int
#     y: int
#     z: int

#     def __hash__(self):
#         return hash((self.x, self.y, self.z))

class Filter(BaseModel):
    """
    A Filter is a way to filter items for an inventory.
    """
    stores: Optional[List[str]]
    retrieves: Optional[List[str]]

    def can_store(self, item: str):
        return self.stores is None or item in self.stores

    def can_retrieve(self, item: str):
        return self.retrieves is None or item in self.retrieves

class Inventory(BaseModel):
    """
    
    """
    size: int
    filter: Optional[Filter] = None
    items: Dict[int, str] = Field(default_factory=dict)  # A map from slot to item

    def can_store(self, item: str):
        """
        Returns whether or not the inventory can store the specified item
        """
        return self.filter is None or self.filter.can_store(item)

    def can_retrieve(self, item: str):
        """
        Returns whether or not an agent can retrieve the specified item from the inventory
        """
        return self.filter is None or self.filter.can_retrieve(item)

    def _get_item_counts(self):
        """
        Retrieves the total number of items of each type in the inventory
        """
        item_counts = {}
        for slot, item in self.items.items():
            if item in item_counts:
                item_counts[item] += 1
            else:
                item_counts[item] = 1
        return item_counts

    @property
    def num_counts(self):
        return self._get_item_counts()

    def get_slots_to_retrieve(self, item: str, num: int):
        """
        Retrieves the slots and amount from that slot that need to be retrieved to retrieve the specified number of items.
        We prioritize taking from slots that have the least amount of items
        """
        slots_for_item = [slot for slot in self.items.items() if slot[1] == item]
        slots_for_item.sort(key=lambda slot: slot[0])

        slots_to_retrieve = []
        for slot, item in slots_for_item:
            if num == 0:
                break
            if num >= self.items[slot]:
                slots_to_retrieve.append((slot, self.items[slot]))
                num -= self.items[slot]
            else:
                slots_to_retrieve.append((slot, num))
                num = 0
        
        return slots_to_retrieve
        

class WorldInventory:
    """
    A WorldInventory is a location in the world in which items can be stored or retrieved.
    Note that it does not necessarily actually have an inventory like a chest, it could simply be a place in the world where items are to put put
    """
    def __init__(self, position: StateLocation, inventory: Optional[Inventory] = None, manager: Optional['AgentManager'] = None):
        self.position = position
        self.inventory = inventory
        self.manager = manager

class FuelInventory(WorldInventory):
    """
    A FuelInventory is a WorldInventory that is set up to store fuel items.
    """
    def __init__(self, position: StateLocation, size: int, manager: Optional['AgentManager'] = None):
        inventory = Inventory(size=size, filter=Filter(stores=['minecraft:coal', 'minecraft:charcoal']))
        super().__init__(position, inventory, manager)

class SubWorld:
    """
    SubWorlds are the base element of the world. They all contain their own relative position grid.
    A SubWorld that where the coordinates align with the world grid is called a "RootWorld".

    The main purpose of a SubWorld is to allow for path planning and identifying places to store or retrieve items.
    """
    def __init__(self) -> None:
        self._world_inventories: List[WorldInventory] = {}
        self._fuel_inventories: List[FuelInventory] = {}
        self._occupation_grid: Dict[StateLocation, bool] = {}
        self._detail_grid: Dict[StateLocation, Optional[BlockData]] = {}
        self.key_location_groups: Dict[str, List[Tuple[StateLocation, Any]]]

    def add_world_inventory(self, world_inventory: WorldInventory):
        self._world_inventories.append(world_inventory)

    def add_fuel_inventory(self, fuel_inventory: FuelInventory):
        self._fuel_inventories.append(fuel_inventory)

    def set_block(self, position: StateLocation, block: Optional[BlockData] = None):
        """
        If BlockData is None, then we do not know what the block is, but we know that it is not air
        """
        if block is None:
            self._detail_grid[position] = None
            self._occupation_grid[position] = True
        else:
            self._detail_grid[position] = block
            self._occupation_grid[position] = block.occupied

    def set_blocks(self, blocks: List[Tuple[StateLocation, Optional[BlockData]]]):
        for position, block in blocks:
            self.set_block(position, block)

    def delete_block(self, position: StateLocation):
        if position not in self._detail_grid:
            return # We didn't have this block in the first place
        del self._detail_grid[position]
        del self._occupation_grid[position]

    def in_world(self, position: StateLocation) -> bool:
        return position in self._occupation_grid

    def get_block(self, position: StateLocation) -> Optional[BlockData]:
        if position in self._detail_grid:
            return self._detail_grid[position]
        return None

    def is_occupied(self, position: StateLocation, assume_occupied: bool = True) -> bool:
        if position in self._occupation_grid:
            return self._occupation_grid[position]
        return assume_occupied  # We leave it up to the caller to decide what to do if we don't know

    def add_key_group(self, key: str):
        self.key_location_groups[key] = []

    def add_key_location(self, key: str, position: StateLocation, data: Any):
        if key not in self.key_location_groups:
            raise ValueError(f"Key group {key} does not exist.")
        self.key_location_groups[key].append((position, data))

    def get_key_locations(self, key: str) -> List[Tuple[StateLocation, Any]]:
        if key not in self.key_location_groups:
            raise ValueError(f"Key group {key} does not exist.")
        return self.key_location_groups[key]

    def show(self):
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        import numpy as np
        # Render the world as a voxel grid
        max_x = max([loc.forward for loc in self._occupation_grid.keys()])
        min_x = min([loc.forward for loc in self._occupation_grid.keys()])
        max_y = max([loc.up for loc in self._occupation_grid.keys()])
        min_y = min([loc.up for loc in self._occupation_grid.keys()])
        max_z = max([loc.side for loc in self._occupation_grid.keys()])
        min_z = min([loc.side for loc in self._occupation_grid.keys()])
        ma = np.zeros((max_x - min_x + 1, max_z - min_z + 1, max_y - min_y + 1))
        for loc, occupied in self._occupation_grid.items():
            ma[loc.forward - min_x, loc.side - min_z, loc.up - min_y] = 1 if occupied else 0
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.set_aspect('equal')
        ax.voxels(ma, edgecolor="k")
        ax.set_xlabel('Forward')
        ax.set_ylabel('Side')
        ax.set_zlabel('Up')
        ax.set_xlim(0, max_x - min_x)
        ax.set_ylim(0, max_z - min_z)
        ax.set_zlim(0, max_y - min_y)
        plt.show()

class PathPlanner:
    """
    The PathPlanner is responsible for finding paths between two positions in the world.
    """
    def __init__(self, world: SubWorld):
        self.world = world

    def state_distance(self, start_state: AgentState, end_state: AgentState):
        """
        Returns the distance between two states in the world.
        We take total distance to be the manhattan distance between the two positions, plus 1 - the dot product of the two orientations.
        """
        if end_state.orientation is None:
            return start_state.location.distance(end_state.location)
        return start_state.location.distance(end_state.location) + 1 - start_state.orientation.dot(end_state.orientation)
        
    def get_free_state_neighbors(self, state: AgentState, assume_occupied: bool = True):
        """
        Free state neighbors are neighbors of state that are in and not occupied by the world
        """
        return [neighbor for neighbor in state.neighbors() if not self.world.is_occupied(neighbor.location, assume_occupied=assume_occupied)]

    def reject_out_of_plane_factory(self, start_state: AgentState):
        """
        Returns a function that rejects states that are not in the same plane as start_state
        """
        def reject_out_of_plane(state: AgentState):
            return state.location.up != start_state.location.up
        return reject_out_of_plane

    def _run_state_A_star(self,
        start_state: AgentState,
        at_goal: Callable[[AgentState], bool],  # Returns true if the state is a goal state
        heuristic: Callable[[AgentState], float],  # Returns the heuristic distance from the state to the goal. Should underestimate the distance
        assume_occupied: bool = True,  # If true, then we assume that any unknown blocks are occupied. This is good if we want to ensure the agent doesn't get stuck, but is restrictive if the agent is a scanner
        reject_neighbors: Optional[Callable[[AgentState], bool]] = None  
    ) -> Optional[List[AgentState]]:
        """
        Runs A* on the state space graph
        TODO: We are in an infinite world so this can cause an infinite loop.
            To solve this, we need to run A* from both the start and end states and stop when we find a common state.
            If one or the other runs out of states, then we know that there is no path.
            This works since there are no infinite walls in the world so one or the other is enclosed if there is no path
        """
        if not self.world.in_world(start_state.location):
            print(f"Start state {start_state} is not in the world")
            return None

        open = PriorityQueue()
        closed = {}
        open.put((0, (start_state, None, 0)))
        while (not open.empty()):
            _, (state, parent, path_cost) = open.get()
            # print(f"Exploring {state} with parent {parent} and path cost {path_cost}")
            if state in closed:
                continue
            if at_goal(state):
                path = [state]
                while parent is not None:
                    path.append(parent)
                    parent = closed[parent]
                path.reverse()
                return path
            
            closed[state] = parent
            for neighbor in self.get_free_state_neighbors(state, assume_occupied):
                # if at_goal(neighbor):
                #     print("Found goal state as neighbor")
                if reject_neighbors is not None and reject_neighbors(neighbor):
                    # print(f"\tRejecting neighbor {neighbor}")
                    continue
                if neighbor not in closed:
                    # print(f"\tAdding neighbor {neighbor}")
                    open.put((path_cost + 1 + heuristic(neighbor), (neighbor, state, path_cost + 1)))

        return None

    def find_state_path(self, start_state: AgentState, end_state: AgentState, assume_occupied: bool = True, reject_neighbors: Optional[Callable[[AgentState], bool]] = None):
        """
        Finds the shortest path in time between two states by taking into account location and orientation changes in the graph search
        """
        if not self.world.in_world(end_state.location):
            print(f"End state {end_state} is not in world")
            return None

        def at_goal(state: AgentState):
            if end_state.orientation is not None:
                return state == end_state
            else:
                return state.location == end_state.location

        heuristic = lambda state: self.state_distance(state, end_state)

        return self._run_state_A_star(start_state, at_goal, heuristic, assume_occupied, reject_neighbors)

    def find_state_path_to_any(self, start_state: AgentState, end_states: List[AgentState], assume_occupied: bool = True, reject_neighbors: Optional[Callable[[AgentState], bool]] = None):
        """
        Finds the shortest path in time between a start state and any of a list of end states. This is useful for doing something like finding the closest fuel inventory to the agent.
        This task can be conceptualized as adding an edge of 0 weight between every end state and some imagined "goal". This immediately works with Dijkstra's algorithm, but we can also use A* by choosing a valid heuristic.
        One such valid heuristic is the minimum distance to any of the end states as that still underestimates the true minimum distance.
        """
        def at_goal(state: AgentState):
            for end_state in end_states:
                if end_state.orientation is not None:
                    if state == end_state:
                        return True
                else:
                    if state.location == end_state.location:
                        return True
            return False

        heuristic = lambda state: min([self.state_distance(state, end_state) for end_state in end_states])

        return self._run_state_A_star(start_state, at_goal, heuristic, assume_occupied, reject_neighbors)

def test():
    from models.__agent_models import AgentState, StateLocation, StateOrientation
    test_world = SubWorld()
    path_planner = PathPlanner(test_world)
    
    for x in range(9):
        for z in range(9):
            test_world.set_block(StateLocation(side=x, up=0, forward=z), BlockData(name="minecraft:air"))
    start_state = AgentState(location=StateLocation(forward=0, up=0, side=0), orientation=StateOrientation(forward=1, up=0, side=0))
    end_state = AgentState(location=StateLocation(forward=8, up=0, side=8))

    def print_neighbors(state: AgentState):
        neighbors = path_planner.get_free_state_neighbors(state)
        print(f"{state} neighbors:")
        for neighbor in neighbors:
            print(f"\t{neighbor}")
        print()

    print_neighbors(start_state)

    test_state = AgentState(location=StateLocation(forward=1, up=0, side=0), orientation=StateOrientation(forward=0, up=0, side=1))
    print_neighbors(test_state)

    path = path_planner.find_state_path(start_state, end_state)

    if path is None:
        print("No path found")
        return

    print("Path found:")
    for state in path:
        print(state)

if __name__ == "__main__":
    test()