import boto3
import os
import json
from botocore.exceptions import ClientError

def probe_all_models(region):
    print(f"\n================ Listing and Probing All Models in {region} ================")
    try:
        session = boto3.Session()
        bedrock = session.client("bedrock", region_name=region)
        runtime = session.client("bedrock-runtime", region_name=region)
        
        models = bedrock.list_foundation_models().get("modelSummaries", [])
        print(f"Total foundation models in {region}: {len(models)}")
        
        # We will test all models that support TEXT input and have active status
        text_models = []
        for m in models:
            # Check if it's text-to-text or similar
            if "TEXT" in m.get("inputModalities", []) and "TEXT" in m.get("outputModalities", []):
                text_models.append(m["modelId"])
        
        print(f"Text models to probe: {len(text_models)}")
        
        # Test a standard dummy request depending on provider
        success_models = []
        for model in text_models:
            # Format payload based on provider
            body = None
            if "anthropic" in model:
                body = json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": [{"type": "text", "text": "Hi"}]}]
                })
            elif "meta" in model:
                body = json.dumps({
                    "prompt": "Hi",
                    "max_gen_len": 10
                })
            elif "cohere" in model:
                body = json.dumps({
                    "prompt": "Hi",
                    "max_tokens": 10
                })
            elif "amazon" in model:
                body = json.dumps({
                    "inputText": "Hi",
                    "textGenerationConfig": {"maxTokenCount": 10}
                })
            elif "mistral" in model:
                body = json.dumps({
                    "prompt": "<s>[INST] Hi [/INST]",
                    "max_tokens": 10
                })
            
            if not body:
                # Skip unknown providers or fallback to basic prompt
                continue
                
            try:
                runtime.invoke_model(modelId=model, body=body)
                print(f"  [SUCCESS] {model}")
                success_models.append(model)
            except ClientError as ce:
                msg = ce.response.get("Error", {}).get("Message", str(ce))
                # print(f"  [FAILED] {model} : {msg}")
            except Exception as e:
                # print(f"  [ERROR] {model} : {e}")
                pass
                
        print(f"Successfully invoked models in {region}: {success_models}")
    except Exception as e:
        print(f"Failed to check region {region}: {e}")

if __name__ == "__main__":
    regions = ["us-east-1", "us-west-2", "ap-south-1"]
    for r in regions:
        probe_all_models(r)
