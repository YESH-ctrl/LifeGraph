from typing import Optional, List
from infrastructure.dynamodb.base_repository import BaseRepository
from shared.models.cart_model import CartModel, CartItemModel

class CartRepository(BaseRepository):
    def create_cart(self, cart: CartModel) -> CartModel:
        self.put_item(cart.to_dict())
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
        return cart

    def delete_cart(self, cart_id: str) -> None:
        self.delete_item(f"CART#{cart_id}", "METADATA")

    def list_carts(self) -> List[CartModel]:
        items = self.scan_prefix("CART#", "METADATA")
        return [CartModel.from_dict(item) for item in items]

    def add_item_to_cart(self, item: CartItemModel) -> None:
        self.put_item(item.to_dict())

    def get_cart_items(self, cart_id: str) -> List[CartItemModel]:
        items = self.query_by_pk(f"CART#{cart_id}", "CONTAINS#PRODUCT#")
        return [CartItemModel.from_dict(item) for item in items]
