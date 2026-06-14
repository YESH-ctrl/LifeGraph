from typing import Dict, Any
from pydantic import BaseModel

class BedrockResponse(BaseModel):
    content: str
    modelId: str
    usage: Dict[str, Any]
    metadata: Dict[str, Any]
