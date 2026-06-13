from typing import List
from infrastructure.dynamodb.base_repository import BaseRepository

class GraphRepository(BaseRepository):
    def get_mission_requirements(self, mission_id: str) -> List[str]:
        # PK = MISSION#{id}, SK begins_with REQUIRES#
        items = self.query_gsi1_prefix(pk=f"MISSION#{mission_id}", sk_prefix="REQUIRES#")
        # Wait, the prompt says "Store graph edges directly in DynamoDB... PK: MISSION#BIRTHDAY, SK: REQUIRES#PRODUCT#CAKE001"
        # This means we use the main table query, not GSI1.
        items = self.query_prefix(f"MISSION#{mission_id}", "REQUIRES#")
        
        target_ids = []
        for item in items:
            sk = item.get('SK', '')
            parts = sk.split('#')
            if len(parts) >= 3:
                target_ids.append(parts[2])
        return target_ids

    def get_product_dependencies(self, product_id: str) -> List[str]:
        items = self.query_prefix(f"PRODUCT#{product_id}", "DEPENDS_ON#")
        target_ids = []
        for item in items:
            sk = item.get('SK', '')
            parts = sk.split('#')
            if len(parts) >= 3:
                target_ids.append(parts[2])
        return target_ids

    def get_product_substitutes(self, product_id: str) -> List[str]:
        items = self.query_prefix(f"PRODUCT#{product_id}", "SUBSTITUTES_FOR#")
        target_ids = []
        for item in items:
            sk = item.get('SK', '')
            parts = sk.split('#')
            if len(parts) >= 3:
                target_ids.append(parts[2])
        return target_ids
