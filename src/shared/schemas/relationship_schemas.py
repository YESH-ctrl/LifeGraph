from pydantic import BaseModel
from enum import Enum

class RelationshipType(str, Enum):
    REQUIRES = "REQUIRES"
    DEPENDS_ON = "DEPENDS_ON"
    COMPATIBLE_WITH = "COMPATIBLE_WITH"
    SUBSTITUTES_FOR = "SUBSTITUTES_FOR"
    PART_OF_MISSION = "PART_OF_MISSION"

class RelationshipBase(BaseModel):
    source_type: str
    source_id: str
    target_type: str
    target_id: str
    relationship_type: RelationshipType

class RelationshipCreate(RelationshipBase):
    pass

class RelationshipResponse(RelationshipBase):
    id: str
