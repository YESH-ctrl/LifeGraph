from pydantic import BaseModel

class MissionBase(BaseModel):
    name: str
    description: str
    category: str

class MissionCreate(MissionBase):
    mission_id: str

class MissionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None

class MissionResponse(MissionBase):
    mission_id: str
