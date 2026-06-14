from pydantic import BaseModel
from typing import List, Optional

class MissionBase(BaseModel):
    name: str
    description: str
    category: str
    keywords: Optional[List[str]] = []
    synonyms: Optional[List[str]] = []
    intent_examples: Optional[List[str]] = []

class MissionCreate(MissionBase):
    mission_id: str

class MissionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    keywords: Optional[List[str]] = None
    synonyms: Optional[List[str]] = None
    intent_examples: Optional[List[str]] = None

class MissionResponse(MissionBase):
    mission_id: str

