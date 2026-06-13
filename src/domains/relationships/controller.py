import json
from domains.relationships.service import RelationshipService
from domains.relationships.schemas import RelationshipCreate, RelationshipResponse

class RelationshipController:
    def __init__(self):
        self.service = RelationshipService()

    def create_relationship(self, event: dict) -> dict:
        body = json.loads(event.get('body', '{}'))
        schema = RelationshipCreate(**body)
        rel = self.service.create_relationship(schema)
        response = RelationshipResponse(
            id=rel.id,
            source_type=rel.source_type,
            source_id=rel.source_id,
            target_type=rel.target_type,
            target_id=rel.target_id,
            relationship_type=rel.relationship_type
        )
        return {
            "statusCode": 201,
            "body": json.dumps({"success": True, "data": response.model_dump()})
        }

    def delete_relationship(self, event: dict) -> dict:
        relationship_id = event['pathParameters']['id']
        self.service.delete_relationship(relationship_id)
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": {}})
        }

    def list_relationships(self, event: dict) -> dict:
        relationships = self.service.list_relationships()
        response = [
            RelationshipResponse(
                id=r.id,
                source_type=r.source_type,
                source_id=r.source_id,
                target_type=r.target_type,
                target_id=r.target_id,
                relationship_type=r.relationship_type
            ).model_dump()
            for r in relationships
        ]
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": response})
        }
