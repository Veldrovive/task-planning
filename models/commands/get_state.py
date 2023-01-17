from pydantic import BaseModel
from models.__agent_models import AgentState

class GetStateReqData(BaseModel):
    pass

class GetStateResData(AgentState):
    pass