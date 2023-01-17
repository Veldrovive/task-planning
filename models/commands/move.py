from pydantic import BaseModel, root_validator
from models.__agent_models import StateLocation, StateOrientation

class MoveTo(StateLocation):
    pass

class MoveBy(StateLocation):
    pass

class FaceTo(StateOrientation):
    pass


class MoveReqData(BaseModel):
    moveTo: MoveTo = None
    moveBy: MoveBy = None
    faceTo: FaceTo = None

    @root_validator
    def check_move_req_data(cls, values):
        moveTo = values.get("moveTo")
        moveBy = values.get("moveBy")
        faceTo = values.get("faceTo")
        if moveTo is None and moveBy is None and faceTo is None:
            raise ValueError("One of moveTo, moveBy, or faceTo must be specified")
        if moveTo is not None and moveBy is not None:
            raise ValueError("Only one of moveTo or moveBy can be specified")
        return values

class MoveResData(BaseModel):
    pass