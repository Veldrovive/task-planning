from pydantic import BaseModel
from enum import Enum
from typing import Any, List
from models.__world_models import LuaList

class FieldID(Enum):
    """
    The set of fields that the agent should be able to initialize
    """
    ID = "id"
    LABEL = "label"

class FieldRequirement(BaseModel):
    # Sent with the request for initialization
    fieldId: FieldID
    fieldName: str
    fieldDescription: str

class FieldValue(BaseModel):
    # Expected as the response for initialized fields
    fieldId: FieldID
    value: Any

class InitializeReqData(BaseModel):
    requiredFields: List[FieldRequirement]

class InitializeResData(BaseModel):
    initializedFields: LuaList[FieldValue]