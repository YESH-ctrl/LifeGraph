import boto3
import os
import json
from botocore.exceptions import ClientError

def test_converse(model_id, region="ap-south-1"):
    print(f"Testing Converse API for model {model_id} in {region}...")
    try:
        session = boto3.Session()
        client = session.client("bedrock-runtime", region_name=region)
        
        system_prompts = [{"text": "You are a helpful assistant."}]
        messages = [
            {
                "role": "user",
                "content": [{"text": "Hello, respond with exactly 'ACTIVE' if you receive this."}]
            }
        ]
        
        response = client.converse(
            modelId=model_id,
            messages=messages,
            system=system_prompts,
            inferenceConfig={
                "maxTokens": 20,
                "temperature": 0.1
            }
        )
        
        text = response["output"]["message"]["content"][0]["text"]
        print(f"  [SUCCESS] response: {text}")
        return True
    except Exception as e:
        print(f"  [FAILED] {e}")
        return False

if __name__ == "__main__":
    test_converse("meta.llama3-8b-instruct-v1:0")
    test_converse("mistral.mistral-large-2402-v1:0")
