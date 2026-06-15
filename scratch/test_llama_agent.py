import os
import sys
import json
import boto3
from pydantic import BaseModel
from typing import List

# Setup PYTHONPATH to include src
sys.path.append(os.path.abspath("src"))

from shared.ai.ai_gateway import AIGateway
from shared.ai.schemas import DecisionDelta, MissionAnalysisOutput, CartAnalysisOutput
from shared.ai.model_router import ModelRouter

def test_llama_agent_run():
    # Force BEDROCK_LIVE mode
    os.environ["MODE"] = "BEDROCK_LIVE"
    os.environ["AWS_REGION"] = "ap-south-1"
    
    # Temporarily override ModelRouter to use Llama 3 models
    ModelRouter.SONNET = "meta.llama3-70b-instruct-v1:0"
    ModelRouter.HAIKU = "meta.llama3-8b-instruct-v1:0"
    ModelRouter.ROUTING_MAP = {
        "mission": ModelRouter.HAIKU,
        "cart": ModelRouter.SONNET,
        "verification": ModelRouter.HAIKU,
        "risk": ModelRouter.HAIKU,
        "regret": ModelRouter.HAIKU,
        "simulation": ModelRouter.SONNET,
        "auditor": ModelRouter.SONNET
    }
    
    print("Testing manual run of Mission Agent prompt via Llama 3 8B with maxTokens=2048...")
    
    gateway = AIGateway()
    
    # Create system prompt and user prompt
    prompt = gateway.prompts.render("mission", "1.0.0", query="Month groceries", original_json="{}")
    system_prompt = "System prompt for mission agent. Output raw JSON matches only."
    
    session = boto3.Session()
    client = session.client("bedrock-runtime", region_name="ap-south-1")
    
    try:
        response = client.converse(
            modelId="meta.llama3-8b-instruct-v1:0",
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            system=[{"text": system_prompt}],
            inferenceConfig={
                "temperature": 0.1,
                "maxTokens": 2048
            }
        )
        text = response["output"]["message"]["content"][0]["text"]
        print("Response received from Llama 3 8B:")
        print(text)
        
        # Try to parse it
        parsed = gateway.claude.parse_json_response(text, DecisionDelta[MissionAnalysisOutput])
        print("Successfully parsed into Pydantic model!")
        print(parsed.model_dump_json(indent=2))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_llama_agent_run()
