from pydantic import BaseModel, root_validator
from typing import Optional, List, Any

class StateLocation(BaseModel):
    forward: int = 0
    side: int = 0
    up: int = 0

    def distance(self, other: 'StateLocation') -> int:
        return abs(self.forward - other.forward) + abs(self.side - other.side) + abs(self.up - other.up)

    def __str__(self) -> str:
        return f"l=({self.forward},{self.side},{self.up})"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, StateLocation):
            return False
        return self.forward == other.forward and self.side == other.side and self.up == other.up

    def __hash__(self) -> int:
        return hash(('location', self.forward, self.side, self.up))

class StateOrientation(BaseModel):
    forward: int = 0
    side: int = 0
    up: int = 0

    def dot(self, other: 'StateOrientation') -> int:
        return self.forward * other.forward + self.side * other.side + self.up * other.up

    @root_validator
    def check_face_to(cls, values):
        forward = values.get("forward")
        side = values.get("side")
        up = values.get("up")
        if forward is None or side is None or up is None:
            raise ValueError("All values must be specified")
        if forward == 0 and side == 0:
            raise ValueError("One of forward or side must be non-zero")
        if forward != 0 and side != 0:
            raise ValueError("Only one of forward or side can be non-zero")
        if max(abs(forward), abs(side)) != 1:
            raise ValueError("Forward and side must be -1, 0, or 1")
        if up != 0:
            raise ValueError("Up must be 0")
        return values

    def __str__(self) -> str:
        return f"o=({self.forward},{self.side},{self.up})"
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, StateOrientation):
            return False
        return self.forward == other.forward and self.side == other.side and self.up == other.up

    def __hash__(self) -> int:
        return hash(('orientation', self.forward, self.side, self.up))

class AgentState(BaseModel):
    location: StateLocation
    orientation: Optional[StateOrientation]  # We may not care what the orientation is if we are specifying a state to move to

    def neighbors(self) -> List['AgentState']:
        """
        Retrieves all states that the agent can move to in a single movement.
        These come in two classes:
        1. States that are in the same location as the current state, but with a different orientation
        2. States that are in a different location than the current state, but with the same orientation
        """
        # Location neighbors are forward, backward, up, or down
        # location_neighbors = [
        #     AgentState(location=StateLocation(forward=self.location.forward + 1, side=self.location.side, up=self.location.up), orientation=self.orientation.copy()),
        #     AgentState(location=StateLocation(forward=self.location.forward - 1, side=self.location.side, up=self.location.up), orientation=self.orientation.copy()),
        #     AgentState(location=StateLocation(forward=self.location.forward, side=self.location.side, up=self.location.up + 1), orientation=self.orientation.copy()),
        #     AgentState(location=StateLocation(forward=self.location.forward, side=self.location.side, up=self.location.up - 1), orientation=self.orientation.copy()),
        # ]
        location_neighbors = [
            AgentState(location=StateLocation(forward=self.location.forward + self.orientation.forward, side=self.location.side + self.orientation.side, up=self.location.up), orientation=self.orientation.copy()),
            # AgentState(location=StateLocation(forward=self.location.forward - self.orientation.forward, side=self.location.side - self.orientation.side, up=self.location.up), orientation=self.orientation.copy()),
            AgentState(location=StateLocation(forward=self.location.forward, side=self.location.side, up=self.location.up + 1), orientation=self.orientation.copy()),
            AgentState(location=StateLocation(forward=self.location.forward, side=self.location.side, up=self.location.up - 1), orientation=self.orientation.copy())
        ]

        # Orientation neighbors are left turn or right turn
        # We can compute a turn using a C2 rotation matrix
        positive_turn = StateOrientation(forward=self.orientation.side, side=-self.orientation.forward, up=self.orientation.up)
        negative_turn = StateOrientation(forward=-self.orientation.side, side=self.orientation.forward, up=self.orientation.up)
        orientation_neighbors = [
            AgentState(location=self.location.copy(), orientation=positive_turn),
            AgentState(location=self.location.copy(), orientation=negative_turn),
        ]

        return location_neighbors + orientation_neighbors

    def __str__(self) -> str:
        if self.orientation is None:
            return self.location.__str__()
        return f"{self.location.__str__()} {self.orientation.__str__()}"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, AgentState):
            return False
        return self.location == other.location and self.orientation == other.orientation

    def __hash__(self) -> int:
        return hash(('state', self.location, self.orientation))

    def __lt__(self, other: Any) -> bool:
        return False

    def __gt__(self, other: Any) -> bool:
        return False
