from typing import Dict, Any, List

class ProductModel:
    def __init__(self, id: str, name: str, price: float, stock: int, category: str,
                title: str = "", brand: str = "", subcategory: str = "", description: str = "",
                mrp: float = 0.0, rating: float = 0.0, reviews: int = 0, image: str = "",
                prime: bool = False, deliveryDays: int = 3, semanticTags: List[str] = None,
                missionHints: List[Dict[str, Any]] = None, embeddingText: str = ""):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock
        self.category = category
        self.title = title or name
        self.brand = brand
        self.subcategory = subcategory
        self.description = description
        self.mrp = mrp or price
        self.rating = rating
        self.reviews = reviews
        self.image = image
        self.prime = prime
        self.deliveryDays = deliveryDays
        self.semanticTags = semanticTags or []
        self.missionHints = missionHints or []
        self.embeddingText = embeddingText

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProductModel':
        name = data.get('name') or data.get('title') or ''
        title = data.get('title') or data.get('name') or ''
        return cls(
            id=data.get('id', ''),
            name=name,
            price=float(data.get('price', 0.0)),
            stock=int(data.get('stock', 0)),
            category=data.get('category', ''),
            title=title,
            brand=data.get('brand', ''),
            subcategory=data.get('subcategory', ''),
            description=data.get('description', ''),
            mrp=float(data.get('mrp', 0.0)),
            rating=float(data.get('rating', 0.0)),
            reviews=int(data.get('reviews', 0)),
            image=data.get('image', ''),
            prime=bool(data.get('prime', False)),
            deliveryDays=int(data.get('deliveryDays', 3)),
            semanticTags=data.get('semanticTags', []),
            missionHints=data.get('missionHints', []),
            embeddingText=data.get('embeddingText', '')
        )

    def to_dict(self) -> Dict[str, Any]:
        from decimal import Decimal
        return {
            'PK': f"PRODUCT#{self.id}",
            'SK': "METADATA",
            'entityType': "PRODUCT",
            'id': self.id,
            'name': self.name,
            'title': self.title,
            'brand': self.brand,
            'price': Decimal(str(self.price)),
            'mrp': Decimal(str(self.mrp)),
            'stock': self.stock,
            'category': self.category,
            'subcategory': self.subcategory,
            'description': self.description,
            'rating': Decimal(str(self.rating)),
            'reviews': self.reviews,
            'image': self.image,
            'prime': self.prime,
            'deliveryDays': self.deliveryDays,
            'semanticTags': self.semanticTags,
            'missionHints': self.missionHints,
            'embeddingText': self.embeddingText,
            'GSI1PK': f"CATEGORY#{self.category}",
            'GSI1SK': f"PRODUCT#{self.id}"
        }
