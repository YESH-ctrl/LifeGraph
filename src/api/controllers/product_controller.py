import json
from shared.services.product_service import ProductService
from shared.schemas.product_schemas import ProductCreate, ProductUpdate, ProductResponse

class ProductController:
    def __init__(self):
        self.service = ProductService()

    def create_product(self, event: dict) -> dict:
        body = json.loads(event.get('body', '{}'))
        schema = ProductCreate(**body)
        product = self.service.create_product(schema)
        response = ProductResponse(
            id=product.id, 
            name=product.name, 
            price=product.price, 
            stock=product.stock, 
            category=product.category
        )
        return {
            "statusCode": 201,
            "body": json.dumps({"success": True, "data": response.model_dump()})
        }

    def get_product(self, event: dict) -> dict:
        product_id = event['pathParameters']['id']
        product = self.service.get_product(product_id)
        response = ProductResponse(
            id=product.id, 
            name=product.name, 
            price=product.price, 
            stock=product.stock, 
            category=product.category
        )
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": response.model_dump()})
        }

    def update_product(self, event: dict) -> dict:
        product_id = event['pathParameters']['id']
        body = json.loads(event.get('body', '{}'))
        schema = ProductUpdate(**body)
        product = self.service.update_product(product_id, schema)
        response = ProductResponse(
            id=product.id, 
            name=product.name, 
            price=product.price, 
            stock=product.stock, 
            category=product.category
        )
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": response.model_dump()})
        }

    def delete_product(self, event: dict) -> dict:
        product_id = event['pathParameters']['id']
        self.service.delete_product(product_id)
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": {}})
        }

    def list_products(self, event: dict) -> dict:
        query = event.get('queryStringParameters') or {}
        category = query.get('category')
        if category:
            products = self.service.list_products_by_category(category)
        else:
            products = self.service.list_products()
        
        response = [
            ProductResponse(
                id=p.id, name=p.name, price=p.price, stock=p.stock, category=p.category
            ).model_dump() for p in products
        ]
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": response})
        }
