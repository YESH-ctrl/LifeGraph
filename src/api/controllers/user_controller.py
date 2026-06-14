import json
from foundation.shared.services.user_service import UserService
from foundation.shared.schemas.user_schemas import UserCreate, UserUpdate, UserResponse

class UserController:
    def __init__(self):
        self.service = UserService()

    def create_user(self, event: dict) -> dict:
        body = json.loads(event.get('body', '{}'))
        schema = UserCreate(**body)
        user = self.service.create_user(schema)
        response = UserResponse(id=user.id, name=user.name, email=user.email)
        return {
            "statusCode": 201,
            "body": json.dumps({"success": True, "data": response.model_dump()})
        }

    def get_user(self, event: dict) -> dict:
        user_id = event['pathParameters']['id']
        user = self.service.get_user(user_id)
        response = UserResponse(id=user.id, name=user.name, email=user.email)
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": response.model_dump()})
        }

    def update_user(self, event: dict) -> dict:
        user_id = event['pathParameters']['id']
        body = json.loads(event.get('body', '{}'))
        schema = UserUpdate(**body)
        user = self.service.update_user(user_id, schema)
        response = UserResponse(id=user.id, name=user.name, email=user.email)
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": response.model_dump()})
        }

    def delete_user(self, event: dict) -> dict:
        user_id = event['pathParameters']['id']
        self.service.delete_user(user_id)
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": {}})
        }

    def list_users(self, event: dict) -> dict:
        users = self.service.list_users()
        response = [UserResponse(id=u.id, name=u.name, email=u.email).model_dump() for u in users]
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": response})
        }
