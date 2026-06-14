import sys
import os
import requests

sys.path.insert(0, os.path.abspath(os.path.join('d:/LifeGraph', 'src')))

from foundation.shared.repositories.cart_repository import CartRepository
from foundation.shared.models.cart_model import CartModel, CartItemModel

repo = CartRepository()
BASE_URL = "http://127.0.0.1:8000"

scenarios = {
    "CHICKEN_BIRYANI": {
        "intent": "I'm cooking chicken biryani for dinner tonight.",
        "cart": ["Basmati Rice", "Chicken", "Cooking Oil"]
    },
    "MOVIE_NIGHT": {
        "intent": "Having some friends over to watch a movie.",
        "cart": ["Popcorn", "Soft Drinks", "Nachos"]
    },
    "ROAD_TRIP": {
        "intent": "Heading out for a long drive this weekend.",
        "cart": ["Snacks", "Water Bottles", "Sunglasses"]
    },
    "BABY_CARE": {
        "intent": "Need to restock on some essentials for the baby.",
        "cart": ["Diapers", "Baby Wipes", "Baby Powder"]
    },
    "HOUSE_PARTY": {
        "intent": "Throwing a big party at my place tonight.",
        "cart": ["Paper Plates", "Cups", "Ice Cubes"]
    }
}

stories = []

for idx, (mission, data) in enumerate(scenarios.items()):
    cart_id = f"DEMO_CART_STORY_{idx}"
    
    try:
        repo.delete_cart(cart_id)
    except:
        pass
        
    repo.create_cart(CartModel(id=cart_id, user_id='demo_user'))
    for item in data["cart"]:
        repo.add_item_to_cart(CartItemModel(cart_id=cart_id, product_id=item, quantity=1))
        
    payload = {
        "missionId": mission,
        "cartId": cart_id,
        "userIntent": data["intent"]
    }
    
    headers = {'Connection': 'close'}
    checkout_resp = requests.post(f"{BASE_URL}/workflows/checkout", json=payload, headers=headers)
    
    if checkout_resp.status_code == 200:
        wf_data = checkout_resp.json().get('data', {})
        
        ver_res = requests.post(f'{BASE_URL}/verification/verify', json=payload, headers=headers).json().get('data', {})
        v_score = ver_res.get('verification_score', 0)
        m_items = ver_res.get('missing_items', [])
        
        risk_payload = {'verification_score': v_score, 'missing_items': m_items}
        risk_res = requests.post(f'{BASE_URL}/risk/analyze', json=risk_payload, headers=headers).json().get('data', {})
        risk_score = risk_res.get('risk_score', 0)
        
        story = f"## Mission: {mission}\n\n"
        story += f"**1. User Intent:** {data['intent']}\n"
        story += f"**2. Cart:** {', '.join(data['cart'])}\n"
        story += f"**3. Missing Items:** {', '.join(m_items) if m_items else 'None'}\n"
        story += f"**4. Verification Score:** {v_score}\n"
        story += f"**5. Risk Score:** {risk_score}\n"
        story += f"**6. Prevention Decision:** {'Block' if not wf_data.get('checkout_allowed', True) else 'Allow'}\n"
        story += f"**7. Final Outcome Message:** {wf_data.get('message', '')}\n\n"
        
        stories.append(story)
        
artifact_path = r"C:\Users\srava\.gemini\antigravity\brain\de5955b7-0949-4384-9d8f-9ea18b737cd8\demo_stories.md"
with open(artifact_path, "w") as f:
    f.write("# LifeGraph Demo Stories\n\n")
    f.write("".join(stories))

print(f"Generated stories and saved to {artifact_path}")
