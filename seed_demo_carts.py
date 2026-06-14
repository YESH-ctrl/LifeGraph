import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join('d:/LifeGraph', 'src')))

from foundation.shared.repositories.cart_repository import CartRepository
from foundation.shared.models.cart_model import CartModel, CartItemModel

def seed():
    repo = CartRepository()
    
    carts_data = {
        'CART_A_EMPTY': [],
        'CART_B_PARTIAL': ['CAKE001', 'CANDLE001'],
        'CART_C_COMPLETE': ['CAKE001', 'CANDLE001', 'DRINK001', 'SNACK001']
    }
    
    print("Deleting old carts...")
    for cart_id in carts_data.keys():
        try:
            repo.delete_cart(cart_id)
            # Also delete items by getting them and deleting
            items = repo.get_cart_items(cart_id)
            for item in items:
                repo.delete_item(f"CART#{cart_id}", f"CONTAINS#PRODUCT#{item.product_id}")
        except Exception as e:
            print("Delete error:", e)
    
    print("Creating new carts...")
    for cart_id, items in carts_data.items():
        print(f"Creating {cart_id}...")
        repo.create_cart(CartModel(id=cart_id, user_id='demo_user'))
        for item in items:
            repo.add_item_to_cart(CartItemModel(cart_id=cart_id, product_id=item, quantity=1))
            
    print("Verification:")
    for cart_id in carts_data.keys():
        c = repo.get_cart(cart_id)
        i = repo.get_cart_items(cart_id)
        print(f"{cart_id}:", c, "Items:", len(i))

if __name__ == '__main__':
    seed()
