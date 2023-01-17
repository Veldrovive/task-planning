from pydantic import BaseModel

class WriteFileReqData(BaseModel):
    filepath: str
    contents: str

class WriteFileResData(BaseModel):
    pass