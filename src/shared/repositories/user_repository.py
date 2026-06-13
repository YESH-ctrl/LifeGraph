from typing import Optional
from infrastructure.dynamodb.base_repository import BaseRepository
from shared.models.user_model import UserModel

class UserRepository(BaseRepository):
    def create_user(self, user: UserModel) -> UserModel:
        self.put_item(user.to_dict())
        return user

    def get_user(self, user_id: str) -> Optional[UserModel]:
        item = self.get_item(f"USER#{user_id}", "METADATA")
        if item:
            return UserModel.from_dict(item)
        return None

    def update_user(self, user: UserModel) -> UserModel:
        self.put_item(user.to_dict())
        return user

    def delete_user(self, user_id: str) -> None:
        self.delete_item(f"USER#{user_id}", "METADATA")

    def list_users(self) -> list[UserModel]:
        items = self.scan_prefix("USER#", "METADATA")
        return [UserModel.from_dict(item) for item in items]
