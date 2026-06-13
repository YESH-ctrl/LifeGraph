from typing import Dict, Any

class ProductModel:
    def __init__(self, id: str, name: str, price: float, stock: int, category: str):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock
        self.category = category

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProductModel':
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            price=float(data.get('price', 0.0)),
            stock=int(data.get('stock', 0)),
            category=data.get('category', '')
        )

    def to_dict(self) -> Dict[str, Any]:
        from decimal import Decimal
        return {
            'PK': f"PRODUCT#{self.id}",
            'SK': "METADATA",
            'GSI1PK': f"CATEGORY#{self.category}",
            'GSI1SK': f"PRODUCT#{self.id}",
            'id': self.id,
            'name': self.name,
            'price': Decimal(str(self.price)),
            'stock': self.stock,
            'category': self.category
        }
