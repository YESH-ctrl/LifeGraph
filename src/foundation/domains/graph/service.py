from typing import List
from foundation.domains.graph.repository import GraphRepository

class GraphService:
    def __init__(self):
        self.repository = GraphRepository()

    def get_mission_requirements(self, mission_id: str) -> List[str]:
        return self.repository.get_mission_requirements(mission_id)

    def get_product_dependencies(self, product_id: str) -> List[str]:
        return self.repository.get_product_dependencies(product_id)

    def get_product_substitutes(self, product_id: str) -> List[str]:
        return self.repository.get_product_substitutes(product_id)

    def get_health_metrics(self) -> dict:
        return self.repository.get_health_metrics()
