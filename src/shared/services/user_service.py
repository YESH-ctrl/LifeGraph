import uuid
from typing import List, Optional
from shared.repositories.user_repository import UserRepository
from shared.models.user_model import UserModel
from shared.schemas.user_schemas import UserCreate, UserUpdate
from core.exceptions import NotFoundException

class UserService:
    def __init__(self):
        self.repository = UserRepository()

    def create_user(self, data: UserCreate) -> UserModel:
        user_id = str(uuid.uuid4())
        user = UserModel(id=user_id, name=data.name, email=data.email)
        return self.repository.create_user(user)

    def get_user(self, user_id: str) -> UserModel:
        user = self.repository.get_user(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        return user

    def update_user(self, user_id: str, data: UserUpdate) -> UserModel:
        user = self.get_user(user_id)
        if data.name is not None:
            user.name = data.name
        if data.email is not None:
            user.email = data.email
        return self.repository.update_user(user)

    def delete_user(self, user_id: str) -> None:
        self.get_user(user_id) # Check existence
        self.repository.delete_user(user_id)

    def list_users(self) -> List[UserModel]:
        return self.repository.list_users()
