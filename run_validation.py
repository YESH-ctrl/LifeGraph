import urllib.request
import json
import traceback

def hit_endpoint(url, method, payload=None):
    try:
        req = urllib.request.Request(url, method=method)
        req.add_header('Content-Type', 'application/json')
        data = None
        if payload:
            data = json.dumps(payload).encode('utf-8')
        with urllib.request.urlopen(req, data=data) as response:
            res_body = response.read().decode('utf-8')
            return json.loads(res_body)
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode('utf-8')}
    except Exception as e:
        return {"error": str(e)}

print("POST /memory/track")
res = hit_endpoint('http://127.0.0.1:8000/memory/track', 'POST', {"user_id": "USER123", "mission_id": "BIRTHDAY", "mission_name": "Birthday", "status": "ACTIVE"})
print(res)

print("\nGET /memory/history/USER123")
res = hit_endpoint('http://127.0.0.1:8000/memory/history/USER123', 'GET')
print(res)

print("\nGET /memory/active/USER123")
res = hit_endpoint('http://127.0.0.1:8000/memory/active/USER123', 'GET')
print(res)

print("\nPOST /adaptive/analyze")
res = hit_endpoint('http://127.0.0.1:8000/adaptive/analyze', 'POST', {"user_id": "USER123"})
print(res)

print("\nGET /adaptive/profile?user_id=USER123")
res = hit_endpoint('http://127.0.0.1:8000/adaptive/profile?user_id=USER123', 'GET')
print(res)

print("\nPOST /simulator/run")
res = hit_endpoint('http://127.0.0.1:8000/simulator/run', 'POST', {"user_id": "USER123", "mission_id": "BIRTHDAY", "cart_id": "CART123"})
print(res)
