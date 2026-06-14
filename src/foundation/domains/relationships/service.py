from typing import List
from foundation.domains.relationships.repository import RelationshipRepository
from foundation.domains.relationships.models import RelationshipModel
from foundation.domains.relationships.schemas import RelationshipCreate
from foundation.core.exceptions import NotFoundException

class RelationshipService:
    def __init__(self):
        self.repository = RelationshipRepository()

    def create_relationship(self, data: RelationshipCreate) -> RelationshipModel:
        relationship = RelationshipModel(
            source_type=data.source_type,
            source_id=data.source_id,
            target_type=data.target_type,
            target_id=data.target_id,
            relationship_type=data.relationship_type.value
        )
        return self.repository.create_relationship(relationship)

    def get_relationship(self, relationship_id: str) -> RelationshipModel:
        relationship = self.repository.get_relationship(relationship_id)
        if not relationship:
            raise NotFoundException("Relationship", relationship_id)
        return relationship

    def delete_relationship(self, relationship_id: str) -> None:
        self.get_relationship(relationship_id) # Check existence
        self.repository.delete_relationship(relationship_id)

    def list_relationships(self) -> List[RelationshipModel]:
        return self.repository.list_relationships()
