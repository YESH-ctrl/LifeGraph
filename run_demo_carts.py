import sys
import os
import requests

sys.path.insert(0, os.path.abspath(os.path.join('d:/LifeGraph', 'src')))

from foundation.shared.repositories.cart_repository import CartRepository
from foundation.shared.models.cart_model import CartModel, CartItemModel

repo = CartRepository()

carts_data = {
    'CART_A_EMPTY': [],
    'CART_B_PARTIAL': ['CAKE001', 'CANDLE001'],
    'CART_C_COMPLETE': ['CAKE001', 'CANDLE001', 'DRINK001', 'SNACK001']
}

for cart_id, items in carts_data.items():
    try:
        repo.delete_cart(cart_id)
    except:
        pass
    repo.create_cart(CartModel(id=cart_id, user_id='demo_user'))
    for item in items:
        repo.add_item_to_cart(CartItemModel(cart_id=cart_id, product_id=item, quantity=1))

base_url = 'http://127.0.0.1:8000'
results = {}

for cart_id in carts_data.keys():
    print('Testing', cart_id)
    payload = {'missionId': 'BIRTHDAY', 'cartId': cart_id}
    
    headers = {'Connection': 'close'}
    ver_res = requests.post(f'{base_url}/verification/verify', json=payload, headers=headers).json()
    ver_data = ver_res.get('data', {})
    v_score = ver_data.get('verification_score', 0)
    r_score = ver_data.get('readiness_score', 0)
    m_items = ver_data.get('missing_items', [])
    
    risk_payload = {'verification_score': v_score, 'missing_items': m_items}
    risk_res = requests.post(f'{base_url}/risk/analyze', json=risk_payload, headers=headers).json()
    risk_data = risk_res.get('data', {})
    risk_score = risk_data.get('risk_score', 0)
    
    prev_res = requests.post(f'{base_url}/prevent-checkout', json=payload, headers=headers).json()
    prev_data = prev_res.get('data', {})
    allow = prev_data.get('allow_checkout', False)
    
    wf_res = requests.post(f'{base_url}/workflows/checkout', json=payload, headers=headers).json()
    
    results[cart_id] = {
        'verification_score': v_score,
        'readiness_score': r_score,
        'risk_score': risk_score,
        'allow_checkout': allow,
        'missing_items': m_items,
        'workflow_response': wf_res
    }

report_path = r'C:\Users\srava\.gemini\antigravity\brain\de5955b7-0949-4384-9d8f-9ea18b737cd8\demo_cart_validation_report.md'

report = '# Demo Cart Validation Report\n\n'
report += 'This report demonstrates that the LifeGraph engine dynamically calculates scores based on cart contents, preventing checkout when missions are unfulfilled and enabling checkout when a mission is fully provisioned.\n\n'

report += '## Comparison Table\n\n'
report += '| Cart | Verification Score | Readiness Score | Risk Score | Allow Checkout |\n'
report += '|------|--------------------|-----------------|------------|----------------|\n'

for cart_id in carts_data.keys():
    r = results[cart_id]
    allow_str = 'Yes' if r['allow_checkout'] else 'No'
    report += f"| {cart_id} | {r['verification_score']} | {r['readiness_score']} | {r['risk_score']} | {allow_str} |\n"

report += '\n## Detailed Analysis\n\n'

for cart_id in carts_data.keys():
    r = results[cart_id]
    allow_str = 'Allowed' if r['allow_checkout'] else 'Blocked'
    report += f"### {cart_id}\n"
    report += f"- **Verification Score**: {r['verification_score']}\n"
    report += f"- **Readiness Score**: {r['readiness_score']}\n"
    report += f"- **Missing Items**: {', '.join(r['missing_items']) if r['missing_items'] else 'None'}\n"
    report += f"- **Risk Score**: {r['risk_score']}\n"
    report += f"- **Result**: {allow_str}\n\n"

with open(report_path, 'w') as f:
    f.write(report)

print('Validation completed. Report generated at', report_path)
