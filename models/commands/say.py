from pydantic import BaseModel

class SayReqData(BaseModel):
    message: str
    wait: float

class SayResData(BaseModel):
    said: str