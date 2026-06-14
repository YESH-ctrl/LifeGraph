import requests
import json

base_url = "http://127.0.0.1:55142"

def print_res(res):
    try:
        print(json.dumps(res.json(), indent=2))
    except:
        print(res.text)

print("GET /agents/system/status")
r = requests.get(f"{base_url}/agents/system/status")
print_res(r)

print("\nPOST /mission/detect")
r = requests.post(f"{base_url}/mission/detect", json={"query": "Cook biryani"})
print_res(r)

print("\nPOST /mission/execute")
r = requests.post(f"{base_url}/mission/execute", json={
    "userId": "test_user_demo",
    "missionId": "chicken_biryani",
    "cartId": "demo_cart_biryani"
})
print_res(r)
