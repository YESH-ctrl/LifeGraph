import requests
import json
import traceback

def test_endpoint(name, method, url, payload=None):
    print(f"\n--- {name} ---")
    print(f"Request: {method} {url}")
    if payload:
        print(f"Payload: {json.dumps(payload)}")
        
    try:
        res = requests.post(url, json=payload)
        print(f"Status Code: {res.status_code}")
        try:
            body = res.json()
            print(f"Response Body: {json.dumps(body, indent=2)}")
        except:
            body = res.text
            print(f"Response Body: {body}")
    except Exception as e:
        print(f"Exception: {str(e)}")

def main():
    base_url = "http://127.0.0.1:8000"
    
    # Task 3
    test_endpoint("Mission Detection", "POST", f"{base_url}/detect-mission", {"text": "My friend turns 20 tomorrow"})
    
    # Task 4
    test_endpoint("Verification", "POST", f"{base_url}/verification/verify", {"missionId": "BIRTHDAY_PARTY", "cartId": "CART_B_PARTIAL"})
    test_endpoint("Risk", "POST", f"{base_url}/risk/analyze", {"verification_score": 75, "missing_items": ["CANDLES"]})
    test_endpoint("Prevention", "POST", f"{base_url}/prevent-checkout", {"missionId": "BIRTHDAY_PARTY", "cartId": "CART_B_PARTIAL"})

if __name__ == "__main__":
    main()
