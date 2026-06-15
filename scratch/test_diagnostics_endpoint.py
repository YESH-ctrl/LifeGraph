import os
import sys
import json

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from fastapi.testclient import TestClient
from local_app import app

def main():
    client = TestClient(app)
    print("Testing GET /ai/diagnostics endpoint:")
    
    # Run in LOCAL_SIMULATION
    os.environ["MODE"] = "LOCAL_SIMULATION"
    response = client.get("/ai/diagnostics")
    print(f"\nLOCAL_SIMULATION status code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    # Run in BEDROCK_LIVE
    os.environ["MODE"] = "BEDROCK_LIVE"
    response = client.get("/ai/diagnostics")
    print(f"\nBEDROCK_LIVE status code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    main()
