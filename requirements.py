from enum import Enum

class AgentRequirementID(Enum):
    """
    Defines the list of requireable attributes for agents
    """
    CAN_MOVE = "can_move"
    CAN_BREAK = "can_break"
    CAN_PLACE = "can_place"
    HAS_INVENTORY = "has_inventory"
    CAN_SCAN = "can_scan"