import os
from pydantic import BaseModel, Field

class BedrockConfig(BaseModel):
    model_config = {'protected_namespaces': ()}
    
    aws_region: str = Field(default_factory=lambda: os.getenv("AWS_REGION", "ap-south-1"))
    model_id: str = Field(default_factory=lambda: os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0"))
    max_tokens: int = Field(default_factory=lambda: int(os.getenv("BEDROCK_MAX_TOKENS", "1024")))
    temperature: float = Field(default_factory=lambda: float(os.getenv("BEDROCK_TEMPERATURE", "0.7")))
    top_p: float = Field(default_factory=lambda: float(os.getenv("BEDROCK_TOP_P", "1.0")))
