import json
from foundation.domains.graph.service import GraphService

class GraphController:
    def __init__(self):
        self.service = GraphService()

    def get_mission_requirements(self, event: dict) -> dict:
        mission_id = event['pathParameters']['id']
        requirements = self.service.get_mission_requirements(mission_id)
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": requirements})
        }

    def get_product_dependencies(self, event: dict) -> dict:
        product_id = event['pathParameters']['id']
        dependencies = self.service.get_product_dependencies(product_id)
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": dependencies})
        }

    def get_product_substitutes(self, event: dict) -> dict:
        product_id = event['pathParameters']['id']
        substitutes = self.service.get_product_substitutes(product_id)
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": substitutes})
        }
