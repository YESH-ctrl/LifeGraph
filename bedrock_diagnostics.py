import os
import json
import time
import boto3
from botocore.exceptions import ClientError

def test_streaming(client, model_id):
    try:
        messages = [{"role": "user", "content": [{"text": "Hi"}]}]
        response = client.converse_stream(
            modelId=model_id,
            messages=messages,
            inferenceConfig={"maxTokens": 10}
        )
        stream = response.get("stream")
        if stream:
            for event in stream:
                if "contentBlockDelta" in event:
                    return True
        return False
    except Exception as e:
        print(f"Streaming failed: {e}")
        return False

def main():
    print("Running AWS Bedrock Diagnostics...")
    report = {
        "credentials": {
            "loaded": False,
            "access_key_masked": None,
            "error": None
        },
        "region": os.environ.get("AWS_REGION", "ap-south-1"),
        "model_access": [],
        "runtime_invocation": {
            "success": False,
            "model_used": None,
            "latency_sec": 0.0,
            "response": None,
            "error": None
        },
        "streaming_invocation": {
            "success": False,
            "model_used": None,
            "error": None
        }
    }

    # 1. Credentials Check
    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials:
            report["credentials"]["loaded"] = True
            key = credentials.access_key
            report["credentials"]["access_key_masked"] = key[:4] + "*" * (len(key) - 8) + key[-4:]
        else:
            report["credentials"]["error"] = "No credentials retrieved from boto3 session."
    except Exception as e:
        report["credentials"]["error"] = str(e)

    # 2. Bedrock & Bedrock-Runtime Clients
    if report["credentials"]["loaded"]:
        try:
            bedrock_client = session.client("bedrock", region_name=report["region"])
            runtime_client = session.client("bedrock-runtime", region_name=report["region"])
            
            # List available foundation models
            print("Fetching foundation models...")
            models_res = bedrock_client.list_foundation_models()
            model_summaries = models_res.get("modelSummaries", [])
            
            models_to_test = [
                # Llama 3 models (expected working)
                "meta.llama3-8b-instruct-v1:0",
                "meta.llama3-70b-instruct-v1:0",
                # Claude models (expected restricted)
                "apac.anthropic.claude-3-5-sonnet-20241022-v2:0",
                "apac.anthropic.claude-3-5-sonnet-20240620-v1:0",
                "us.anthropic.claude-3-haiku-20240307-v1:0",
                "anthropic.claude-3-haiku-20240307-v1:0"
            ]
            
            print(f"Testing access on {len(models_to_test)} model IDs...")
            available_models = []
            
            for model_id in models_to_test:
                status = "NO_ACCESS"
                error_msg = None
                
                try:
                    # Test invoke using Converse API
                    messages = [{"role": "user", "content": [{"text": "Hi"}]}]
                    runtime_client.converse(
                        modelId=model_id,
                        messages=messages,
                        inferenceConfig={"maxTokens": 5}
                    )
                    status = "ACTIVE"
                except ClientError as ce:
                    error_msg = ce.response.get("Error", {}).get("Message", str(ce))
                    if "Model use case details have not been submitted" in error_msg:
                        status = "PENDING_USE_CASE_FORM"
                    elif "legacy" in error_msg.lower() or "legacy" in ce.response.get("Error", {}).get("Code", "").lower():
                        status = "LEGACY_BLOCKED"
                    elif "not found" in error_msg.lower():
                        status = "MODEL_NOT_FOUND"
                    else:
                        status = "CLIENT_ERROR"
                except Exception as e:
                    status = "ERROR"
                    error_msg = str(e)
                
                access_info = {
                    "model_id": model_id,
                    "provider": "Meta" if "meta" in model_id else "Anthropic",
                    "region": report["region"],
                    "access_status": status,
                    "error": error_msg
                }
                report["model_access"].append(access_info)
                
                available_models.append({
                    "Model ID": model_id,
                    "Provider": "Meta" if "meta" in model_id else "Anthropic",
                    "Region": report["region"],
                    "Access Status": status
                })

            # Save available_models.json (Task 3)
            with open("available_models.json", "w") as f:
                json.dump(available_models, f, indent=2)
            print("Generated available_models.json.")

            # Find an active model for runtime & streaming test
            active_model = next((m["model_id"] for m in report["model_access"] if m["access_status"] == "ACTIVE"), None)
            
            if active_model:
                # Single invoke test
                print(f"Testing active model runtime invocation on '{active_model}'...")
                messages = [{"role": "user", "content": [{"text": "Hello, this is a test diagnostics message. Respond with 'READY'."}]}]
                
                t0 = time.time()
                res = runtime_client.converse(
                    modelId=active_model,
                    messages=messages,
                    inferenceConfig={"maxTokens": 20}
                )
                latency = time.time() - t0
                
                text = res["output"]["message"]["content"][0]["text"]
                
                report["runtime_invocation"]["success"] = True
                report["runtime_invocation"]["model_used"] = active_model
                report["runtime_invocation"]["latency_sec"] = round(latency, 3)
                report["runtime_invocation"]["response"] = text.strip()
                
                # Streaming test
                print(f"Testing active model streaming invocation on '{active_model}'...")
                stream_ok = test_streaming(runtime_client, active_model)
                report["streaming_invocation"]["success"] = stream_ok
                report["streaming_invocation"]["model_used"] = active_model
            else:
                report["runtime_invocation"]["error"] = "No models are ACTIVE and accessible in this region."
                report["streaming_invocation"]["error"] = "No ACTIVE model available for streaming test."
                
        except Exception as e:
            report["runtime_invocation"]["error"] = f"Bedrock diagnostics failure: {e}"

    # Save bedrock_diagnostics_report.json (Task 2)
    with open("bedrock_diagnostics_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("Generated bedrock_diagnostics_report.json.")
    print("Diagnostics complete.")

if __name__ == "__main__":
    main()
