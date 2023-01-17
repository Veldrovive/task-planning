from pydantic import BaseModel

class ChopVerticalTreeReqData(BaseModel):
    replaceSapling: bool = True

class ChopVerticalTreeResData(BaseModel):
    pass