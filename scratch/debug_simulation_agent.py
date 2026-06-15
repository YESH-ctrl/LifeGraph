import os
import sys
import json
import boto3

sys.path.append(os.path.abspath("src"))

from shared.ai.ai_gateway import AIGateway
from shared.ai.schemas import DecisionDelta, SimulationAnalysisOutput
from shared.ai.model_router import ModelRouter

def debug_sim():
    os.environ["MODE"] = "BEDROCK_LIVE"
    os.environ["AWS_REGION"] = "ap-south-1"
    
    ModelRouter.SONNET = "meta.llama3-70b-instruct-v1:0"
    ModelRouter.HAIKU = "meta.llama3-8b-instruct-v1:0"
    
    gateway = AIGateway()
    
    # Render with some sample variables mimicking test_orchestrator_integration
    original_json = json.dumps({"current_success": 70, "optimized_success": 88, "improvement": 18, "recommended_additions": []})
    additions = "[]"
    
    prompt = gateway.prompts.render("simulation", "1.0.0", original_json=original_json, additions=additions)
    system_prompt = (
        f"System prompt for simulation agent. Output raw JSON matches only. "
        "CRITICAL: You MUST set the \"original_output\" field to {} (an empty JSON object) in your JSON response. "
        "Do NOT copy the input JSON or list of items into \"original_output\" under any circumstances. Keep it as {} exactly."
    )
    
    session = boto3.Session()
    client = session.client("bedrock-runtime", region_name="ap-south-1")
    
    try:
        response = client.converse(
            modelId=ModelRouter.SONNET, # meta.llama3-70b-instruct-v1:0
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            system=[{"text": system_prompt}],
            inferenceConfig={
                "temperature": 0.1,
                "maxTokens": 2048
            }
        )
        text = response["output"]["message"]["content"][0]["text"]
        print("--- RAW MODEL RESPONSE ---")
        print(text)
        print("--------------------------")
        
        # Try parse
        parsed = gateway.claude.parse_json_response(text, DecisionDelta[SimulationAnalysisOutput])
        print("Parsed successfully!")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    debug_sim()
