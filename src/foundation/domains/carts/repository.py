from typing import Optional, List
from foundation.infrastructure.dynamodb.base_repository import BaseRepository
from foundation.domains.carts.models import CartModel, CartItemModel

class CartRepository(BaseRepository):
    def create_cart(self, cart: CartModel) -> CartModel:
        self.put_item(cart.to_dict())
        v2_cart = {
            'PK': f"USER#{cart.user_id}",
            'SK': "CART#ACTIVE",
            'entityType': "CART",
            'cartId': cart.id,
            'status': cart.status,
            'detectedMission': cart.detected_mission,
            'readinessScore': cart.readiness_score
        }
        self.table.put_item(Item=v2_cart)
        return cart

    def get_cart(self, cart_id: str) -> Optional[CartModel]:
        item = self.get_item(f"CART#{cart_id}", "METADATA")
        if item:
            return CartModel.from_dict(item)
        return None

    def list_carts_for_user(self, user_id: str) -> List[CartModel]:
        items = self.query_gsi1(f"USER#{user_id}", "CART#")
        return [CartModel.from_dict(item) for item in items]

    def update_cart(self, cart: CartModel) -> CartModel:
        self.put_item(cart.to_dict())
        v2_cart = {
            'PK': f"USER#{cart.user_id}",
            'SK': "CART#ACTIVE",
            'entityType': "CART",
            'cartId': cart.id,
            'status': cart.status,
            'detectedMission': cart.detected_mission,
            'readinessScore': cart.readiness_score
        }
        self.table.put_item(Item=v2_cart)
        return cart

    def delete_cart(self, cart_id: str) -> None:
        cart = self.get_cart(cart_id)
        if cart:
            if cart.user_id:
                try:
                    self.delete_item(f"USER#{cart.user_id}", "CART#ACTIVE")
                except Exception:
                    pass
                try:
                    items = self.query_by_pk(f"USER#{cart.user_id}", "CARTITEM#")
                    for item in items:
                        if "SK" in item:
                            self.delete_item(f"USER#{cart.user_id}", item["SK"])
                except Exception:
                    pass
            try:
                contains_items = self.query_by_pk(f"CART#{cart_id}", "CONTAINS#PRODUCT#")
                for item in contains_items:
                    if "SK" in item:
                        self.delete_item(f"CART#{cart_id}", item["SK"])
            except Exception:
                pass
        self.delete_item(f"CART#{cart_id}", "METADATA")

    def list_carts(self) -> List[CartModel]:
        items = self.scan_prefix("CART#", "METADATA")
        return [CartModel.from_dict(item) for item in items]

    def add_item_to_cart(self, item: CartItemModel) -> None:
        self.put_item(item.to_dict())
        cart = self.get_cart(item.cart_id)
        if cart and cart.user_id:
            v2_item = {
                'PK': f"USER#{cart.user_id}",
                'SK': f"CARTITEM#{item.product_id}",
                'entityType': "CARTITEM",
                'cartId': item.cart_id,
                'product_id': item.product_id,
                'quantity': item.quantity
            }
            self.table.put_item(Item=v2_item)

    def get_cart_items(self, cart_id: str) -> List[CartItemModel]:
        cart = self.get_cart(cart_id)
        if cart and cart.user_id:
            items = self.query_by_pk(f"USER#{cart.user_id}", "CARTITEM#")
            if items:
                cart_items = []
                for item in items:
                    p_id = item.get("product_id") or item.get("SK", "").split("#")[1]
                    cart_items.append(CartItemModel(
                        cart_id=cart_id,
                        product_id=p_id,
                        quantity=int(item.get("quantity", 1))
                    ))
                return cart_items
        items = self.query_by_pk(f"CART#{cart_id}", "CONTAINS#PRODUCT#")
        return [CartItemModel.from_dict(item) for item in items]
