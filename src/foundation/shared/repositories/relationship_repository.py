from typing import Optional, List
from foundation.infrastructure.dynamodb.base_repository import BaseRepository
from foundation.shared.models.relationship_model import RelationshipModel

class RelationshipRepository(BaseRepository):
    def create_relationship(self, relationship: RelationshipModel) -> RelationshipModel:
        self.put_item(relationship.to_dict())
        return relationship

    def get_relationship(self, relationship_id: str) -> Optional[RelationshipModel]:
        try:
            pk, sk = RelationshipModel.from_id(relationship_id)
            item = self.get_item(pk, sk)
            if item:
                return RelationshipModel.from_dict(item)
            return None
        except Exception:
            return None

    def delete_relationship(self, relationship_id: str) -> None:
        try:
            pk, sk = RelationshipModel.from_id(relationship_id)
            self.delete_item(pk, sk)
        except Exception:
            pass

    def list_relationships(self) -> List[RelationshipModel]:
        # Note: Scanning all relationships requires scanning the entire table.
        # For this prototype we will scan and filter out METADATA items.
        response = self.table.scan()
        items = response.get('Items', [])
        
        # Handle pagination
        while 'LastEvaluatedKey' in response:
            response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
            
        # Filter for edge items (not METADATA)
        relationships = []
        for item in items:
            sk = item.get('SK', '')
            if sk != 'METADATA' and '#' in sk and not sk.startswith('CART#'):
                try:
                    relationships.append(RelationshipModel.from_dict(item))
                except Exception:
                    pass
        return relationships
