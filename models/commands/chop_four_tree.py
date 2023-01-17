from pydantic import BaseModel

class ChopFourTreeReqData(BaseModel):
    replaceSapling: bool = True

class ChopFourTreeResData(BaseModel):
    pass