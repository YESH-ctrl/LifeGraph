from typing import List
from infrastructure.dynamodb.base_repository import BaseRepository

class GraphRepository(BaseRepository):
    def get_mission_requirements(self, mission_id: str) -> List[str]:
        items = self.query_by_pk(f"MISSION#{mission_id}", "REQUIRES#")
        
        target_ids = []
        for item in items:
            sk = item.get('SK', '')
            parts = sk.split('#')
            if len(parts) >= 3:
                target_ids.append(parts[2])
        return target_ids

    def get_product_dependencies(self, product_id: str) -> List[str]:
        items = self.query_by_pk(f"PRODUCT#{product_id}", "DEPENDS_ON#")
        target_ids = []
        for item in items:
            sk = item.get('SK', '')
            parts = sk.split('#')
            if len(parts) >= 3:
                target_ids.append(parts[2])
        return target_ids

    def get_product_substitutes(self, product_id: str) -> List[str]:
        items = self.query_by_pk(f"PRODUCT#{product_id}", "SUBSTITUTES_FOR#")
        target_ids = []
        for item in items:
            sk = item.get('SK', '')
            parts = sk.split('#')
            if len(parts) >= 3:
                target_ids.append(parts[2])
        return target_ids
