from typing import Optional
from infrastructure.dynamodb.base_repository import BaseRepository
from domains.adaptive.models import AdaptiveProfileModel

class AdaptiveRepository(BaseRepository):
    """Repository for managing adaptive profile data in DynamoDB."""

    def get_profile(self, user_id: str) -> Optional[AdaptiveProfileModel]:
        item = self.get_item(f"ADAPTIVE#{user_id}", "PROFILE")
        if item:
            return AdaptiveProfileModel.from_dict(item)
        return None

    def save_profile(self, profile: AdaptiveProfileModel) -> AdaptiveProfileModel:
        self.put_item(profile.to_dict())
        return profile

    def update_profile(self, profile: AdaptiveProfileModel) -> AdaptiveProfileModel:
        self.put_item(profile.to_dict())
        return profile
