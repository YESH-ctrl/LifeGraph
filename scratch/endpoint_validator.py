import sys
import json
sys.path.append('src')
from app import handler

def simulate_request(path, payload):
    event = {
        'path': path,
        'httpMethod': 'POST',
        'body': json.dumps(payload),
        'headers': {'Content-Type': 'application/json'}
    }
    try:
        response = handler(event, None)
        return response
    except Exception as e:
        return {'statusCode': 500, 'body': str(e)}

def validate_endpoints():
    report = []
    
    # 1. /mission/detect
    # Requires a query string
    detect_payload = {"query": "I want to cook chicken biryani for 4 people"}
    res = simulate_request('/detect-mission', detect_payload)
    report.append({
        'endpoint': '/mission/detect',
        'payload': detect_payload,
        'response': res,
        'status': 'PASS' if res.get('statusCode') == 200 else 'FAIL'
    })

    # 2. /verification/verify
    # Requires missionId and cartId
    # Assuming cart bb40eea6-212d-4fcd-a3eb-69f38a533c2f or just a fake cart
    from domains.carts.service import CartService
    from domains.carts.schemas import CartCreate
    cart_svc = CartService()
    cart = cart_svc.create_cart(CartCreate(user_id="test_user"))
    cart_id = cart.id

    verify_payload = {"missionId": "chicken_biryani", "cartId": cart_id}
    res = simulate_request('/verification/verify', verify_payload)
    report.append({
        'endpoint': '/verification/verify',
        'payload': verify_payload,
        'response': res,
        'status': 'PASS' if res.get('statusCode') == 200 else 'FAIL'
    })

    # 3. /risk/analyze
    risk_payload = {"userId": "test_user", "cartId": cart_id, "missionId": "chicken_biryani"}
    res = simulate_request('/risk/analyze', risk_payload)
    report.append({
        'endpoint': '/risk/analyze',
        'payload': risk_payload,
        'response': res,
        'status': 'PASS' if res.get('statusCode') == 200 else 'FAIL'
    })

    # 4. /prevent-checkout
    prevent_payload = {"userId": "test_user", "cartId": cart_id}
    res = simulate_request('/prevent-checkout', prevent_payload)
    report.append({
        'endpoint': '/prevent-checkout',
        'payload': prevent_payload,
        'response': res,
        'status': 'PASS' if res.get('statusCode') == 200 else 'FAIL'
    })

    with open('scratch/endpoint_report.json', 'w') as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    validate_endpoints()
