from typing import Dict, Any

class CartModel:
    def __init__(self, id: str, user_id: str, status: str = 'ACTIVE', total: float = 0.0):
        self.id = id
        self.user_id = user_id
        self.status = status
        self.total = total

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CartModel':
        return cls(
            id=data.get('id', ''),
            user_id=data.get('user_id', ''),
            status=data.get('status', 'ACTIVE'),
            total=float(data.get('total', 0.0))
        )

    def to_dict(self) -> Dict[str, Any]:
        from decimal import Decimal
        return {
            'PK': f"CART#{self.id}",
            'SK': "METADATA",
            'GSI1PK': f"USER#{self.user_id}",
            'GSI1SK': f"CART#{self.id}",
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status,
            'total': Decimal(str(self.total))
        }

class CartItemModel:
    def __init__(self, cart_id: str, product_id: str, quantity: int):
        self.cart_id = cart_id
        self.product_id = product_id
        self.quantity = quantity

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CartItemModel':
        return cls(
            cart_id=data.get('cart_id', ''),
            product_id=data.get('product_id', ''),
            quantity=int(data.get('quantity', 0))
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'PK': f"CART#{self.cart_id}",
            'SK': f"CONTAINS#PRODUCT#{self.product_id}",
            'GSI1PK': f"PRODUCT#{self.product_id}",
            'GSI1SK': f"IN_CART#{self.cart_id}",
            'cart_id': self.cart_id,
            'product_id': self.product_id,
            'quantity': self.quantity
        }
