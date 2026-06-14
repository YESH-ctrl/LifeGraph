from typing import Optional, List
from foundation.infrastructure.dynamodb.base_repository import BaseRepository
from foundation.shared.models.product_model import ProductModel

class ProductRepository(BaseRepository):
    def create_product(self, product: ProductModel) -> ProductModel:
        self.put_item(product.to_dict())
        return product

    def get_product(self, product_id: str) -> Optional[ProductModel]:
        item = self.get_item(f"PRODUCT#{product_id}", "METADATA")
        if item:
            return ProductModel.from_dict(item)
        return None

    def update_product(self, product: ProductModel) -> ProductModel:
        self.put_item(product.to_dict())
        return product

    def delete_product(self, product_id: str) -> None:
        self.delete_item(f"PRODUCT#{product_id}", "METADATA")

    def list_products_by_category(self, category: str) -> List[ProductModel]:
        items = self.query_gsi1(f"CATEGORY#{category}")
        return [ProductModel.from_dict(item) for item in items]

    def list_products(self) -> List[ProductModel]:
        items = self.scan_prefix("PRODUCT#", "METADATA")
        return [ProductModel.from_dict(item) for item in items]
