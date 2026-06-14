from pydantic import BaseModel
from enum import Enum
from typing import Optional, List
from enum import Enum

class RelationshipType(str, Enum):
    REQUIRES = "REQUIRES"
    OPTIONAL = "OPTIONAL"
    DEPENDS_ON = "DEPENDS_ON"
    COMPATIBLE_WITH = "COMPATIBLE_WITH"
    SUBSTITUTES_FOR = "SUBSTITUTES_FOR"
    PART_OF_MISSION = "PART_OF_MISSION"
    INTENT_TO = "INTENT_TO"
    SERVES = "SERVES"

class RelationshipBase(BaseModel):
    source_type: str
    source_id: str
    target_type: str
    target_id: str
    relationship_type: RelationshipType
    priority: Optional[str] = None
    weight: Optional[int] = None
    required: Optional[bool] = None
    keywords: Optional[List[str]] = None
    synonyms: Optional[List[str]] = None
    intent_examples: Optional[List[str]] = None
    quantity: Optional[str] = None

class RelationshipCreate(RelationshipBase):
    pass

class RelationshipResponse(RelationshipBase):
    id: str
