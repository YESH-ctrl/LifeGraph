import json
from foundation.shared.services.cart_service import CartService
from foundation.shared.schemas.cart_schemas import CartCreate, CartUpdate, CartAddItem, CartResponse, CartItem

class CartController:
    def __init__(self):
        self.service = CartService()

    def create_cart(self, event: dict) -> dict:
        body = json.loads(event.get('body', '{}'))
        schema = CartCreate(**body)
        cart = self.service.create_cart(schema)
        response = CartResponse(
            id=cart.id, 
            user_id=cart.user_id, 
            status=cart.status, 
            total=cart.total,
            items=[]
        )
        return {
            "statusCode": 201,
            "body": json.dumps({"success": True, "data": response.model_dump()})
        }

    def get_cart(self, event: dict) -> dict:
        cart_id = event['pathParameters']['id']
        data = self.service.get_cart_with_items(cart_id)
        cart = data['cart']
        items = [CartItem(product_id=i.product_id, quantity=i.quantity) for i in data['items']]
        
        response = CartResponse(
            id=cart.id, 
            user_id=cart.user_id, 
            status=cart.status, 
            total=cart.total,
            items=items
        )
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": response.model_dump()})
        }

    def update_cart(self, event: dict) -> dict:
        cart_id = event['pathParameters']['id']
        body = json.loads(event.get('body', '{}'))
        schema = CartUpdate(**body)
        cart = self.service.update_cart(cart_id, schema)
        response = CartResponse(
            id=cart.id, 
            user_id=cart.user_id, 
            status=cart.status, 
            total=cart.total,
            items=[] # Items aren't updated here
        )
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": response.model_dump()})
        }

    def delete_cart(self, event: dict) -> dict:
        cart_id = event['pathParameters']['id']
        self.service.delete_cart(cart_id)
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": {}})
        }

    def list_carts(self, event: dict) -> dict:
        query = event.get('queryStringParameters') or {}
        user_id = query.get('user_id')
        if user_id:
            carts = self.service.list_carts_for_user(user_id)
        else:
            carts = self.service.list_carts()
            
        response = [
            CartResponse(id=c.id, user_id=c.user_id, status=c.status, total=c.total, items=[]).model_dump()
            for c in carts
        ]
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": response})
        }

    def add_item(self, event: dict) -> dict:
        cart_id = event['pathParameters']['id']
        body = json.loads(event.get('body', '{}'))
        schema = CartAddItem(**body)
        self.service.add_item(cart_id, schema)
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": {"message": "Item added to cart"}})
        }
