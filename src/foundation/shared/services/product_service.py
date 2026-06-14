import uuid
from typing import List
from foundation.shared.repositories.product_repository import ProductRepository
from foundation.shared.models.product_model import ProductModel
from foundation.shared.schemas.product_schemas import ProductCreate, ProductUpdate
from foundation.core.exceptions import NotFoundException

class ProductService:
    def __init__(self):
        self.repository = ProductRepository()

    def create_product(self, data: ProductCreate) -> ProductModel:
        product_id = str(uuid.uuid4())
        product = ProductModel(
            id=product_id, 
            name=data.name, 
            price=data.price, 
            stock=data.stock, 
            category=data.category
        )
        return self.repository.create_product(product)

    def get_product(self, product_id: str) -> ProductModel:
        product = self.repository.get_product(product_id)
        if not product:
            raise NotFoundException("Product", product_id)
        return product

    def update_product(self, product_id: str, data: ProductUpdate) -> ProductModel:
        product = self.get_product(product_id)
        if data.name is not None:
            product.name = data.name
        if data.price is not None:
            product.price = data.price
        if data.stock is not None:
            product.stock = data.stock
        if data.category is not None:
            product.category = data.category
        return self.repository.update_product(product)

    def delete_product(self, product_id: str) -> None:
        self.get_product(product_id)
        self.repository.delete_product(product_id)

    def list_products_by_category(self, category: str) -> List[ProductModel]:
        return self.repository.list_products_by_category(category)

    def list_products(self) -> List[ProductModel]:
        return self.repository.list_products()
