from typing import List, Dict, Any, Optional
from foundation.graph.repository import GraphRepository

class GraphService:
    def __init__(self):
        self.repository = GraphRepository()

    def get_mission_requirements(self, mission_id: str) -> List[str]:
        return self.repository.get_mission_requirements(mission_id)

    def get_product_dependencies(self, product_id: str) -> List[str]:
        return self.repository.get_product_dependencies(product_id)

    def get_product_substitutes(self, product_id: str) -> List[str]:
        return self.repository.get_product_substitutes(product_id)

    def get_mission_requirements_weighted(self, mission_id: str) -> List[dict]:
        return self.repository.get_mission_requirements_weighted(mission_id)

    def get_mission_metadata(self, mission_id: str) -> Optional[Dict[str, Any]]:
        return self.repository.get_mission_metadata(mission_id)

    def get_mission_rules(self, mission_id: str) -> List[Dict[str, Any]]:
        return self.repository.get_mission_rules(mission_id)

    def get_mission_parameters(self, mission_id: str) -> List[str]:
        return self.repository.get_mission_parameters(mission_id)

    def get_mission_intents(self, mission_id: str) -> List[str]:
        return self.repository.get_mission_intents(mission_id)

    def get_mission_synonyms(self, mission_id: str) -> List[str]:
        return self.repository.get_mission_synonyms(mission_id)

    def get_product_compatibility(self, product_id: str) -> List[str]:
        return self.repository.get_product_compatibility(product_id)

    def get_health_metrics(self) -> Dict[str, Any]:
        return self.repository.get_health_metrics()

    def get_mission_visualize(self, mission_id: str) -> Dict[str, Any]:
        return self.repository.get_mission_visualize(mission_id)

    def get_product_visualize(self, product_id: str) -> Dict[str, Any]:
        return self.repository.get_product_visualize(product_id)

    def get_mission_coverage(self) -> Dict[str, Any]:
        metrics = self.get_health_metrics()
        # To get more granular detail, ideally we would scan, but we can return stats we have
        # Or run a full scan inside this method
        return self._compute_mission_coverage()

    def get_product_coverage(self) -> Dict[str, Any]:
        return self._compute_product_coverage()

    def get_relationships_audit(self) -> Dict[str, Any]:
        metrics = self.get_health_metrics()
        return {
            "requires_edges": metrics.get("requires_edges", 0),
            "optional_edges": metrics.get("optional_edges", 0),
            "depends_on_edges": metrics.get("depends_on_edges", 0),
            "compatible_with_edges": metrics.get("compatible_with_edges", 0),
            "substitutes_for_edges": metrics.get("substitute_edges", 0),
            "serves_edges": metrics.get("serves_edges", 0),
            "intent_edges": metrics.get("intent_edges", 0) # Assumes INTENT_TO logic
        }

    def validate_graph(self) -> Dict[str, Any]:
        return self._compute_graph_validation()

    def _compute_mission_coverage(self) -> Dict[str, Any]:
        response = self.repository.table.scan()
        items = response.get('Items', [])
        while 'LastEvaluatedKey' in response:
            response = self.repository.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))

        missions = [i for i in items if i.get('PK', '').startswith('MISSION#') and i.get('SK') == 'METADATA']
        total_missions = len(missions)
        
        missions_with_reqs = set()
        missions_with_intents = set()
        missions_with_edges = set()

        for item in items:
            pk = item.get('PK', '')
            sk = item.get('SK', '')
            if pk.startswith('MISSION#'):
                if sk.startswith('REQUIRES#') or sk.startswith('OPTIONAL#'):
                    missions_with_reqs.add(pk)
                    missions_with_edges.add(pk)
                if sk.startswith('INTENT#'):
                    missions_with_intents.add(pk)

        missions_without_edges = []
        missions_with_embeddings = 0
        for m in missions:
            pk = m.get('PK')
            if pk not in missions_with_edges:
                missions_without_edges.append(pk.split('#')[1])
            if m.get('embedding'):
                missions_with_embeddings += 1

        return {
            "total_missions": total_missions,
            "missions_with_requirements": len(missions_with_reqs),
            "missions_with_embeddings": missions_with_embeddings,
            "missions_with_intents": len(missions_with_intents),
            "missions_without_edges": missions_without_edges
        }

    def _compute_product_coverage(self) -> Dict[str, Any]:
        response = self.repository.table.scan()
        items = response.get('Items', [])
        while 'LastEvaluatedKey' in response:
            response = self.repository.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))

        products = [i for i in items if i.get('PK', '').startswith('PRODUCT#') and i.get('SK') == 'METADATA']
        total_products = len(products)
        
        products_with_edges = set()
        for item in items:
            pk = item.get('PK', '')
            sk = item.get('SK', '')
            if pk.startswith('PRODUCT#') and sk != 'METADATA':
                products_with_edges.add(pk)
            # Check target edges
            parts = sk.split('#')
            if len(parts) >= 3 and parts[1] == 'PRODUCT':
                products_with_edges.add(f"PRODUCT#{parts[2]}")

        products_with_embeddings = 0
        products_with_mission_hints = 0
        orphan_products = []

        for p in products:
            pk = p.get('PK')
            if pk not in products_with_edges:
                orphan_products.append(pk.split('#')[1])
            if p.get('embedding') or p.get('embeddingText'):
                products_with_embeddings += 1
            if p.get('missionHints') and len(p.get('missionHints')) > 0:
                products_with_mission_hints += 1

        return {
            "total_products": total_products,
            "products_with_embeddings": products_with_embeddings,
            "products_with_mission_hints": products_with_mission_hints,
            "products_with_relationships": len(products_with_edges),
            "orphan_products": orphan_products
        }

    def _compute_graph_validation(self) -> Dict[str, Any]:
        response = self.repository.table.scan()
        items = response.get('Items', [])
        while 'LastEvaluatedKey' in response:
            response = self.repository.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))

        issues = []
        
        # Track maps
        missions = {}
        products = {}
        mission_edges = {}

        for item in items:
            pk = item.get('PK', '')
            sk = item.get('SK', '')
            if pk.startswith('MISSION#') and sk == 'METADATA':
                missions[pk] = item
                mission_edges[pk] = []
            elif pk.startswith('PRODUCT#') and sk == 'METADATA':
                products[pk] = item
            elif pk.startswith('MISSION#') and sk != 'METADATA':
                if pk not in mission_edges: mission_edges[pk] = []
                mission_edges[pk].append(item)

        # Validate Missions
        for pk, meta in missions.items():
            reqs = [e for e in mission_edges.get(pk, []) if e.get('SK', '').startswith('REQUIRES#')]
            if not reqs:
                issues.append(f"Mission {pk} has missing mission requirements (weighted_requirements == [])")
            if len(mission_edges.get(pk, [])) == 0:
                issues.append(f"Mission {pk} has relationship_count == 0")

        # Validate Products
        for pk, meta in products.items():
            hints = meta.get('missionHints', [])
            emb = meta.get('embeddingText', '')
            if not hints or len(hints) == 0:
                issues.append(f"Product {pk} has missionHints == []")
            if not emb or emb.strip() == "":
                issues.append(f"Product {pk} has embeddingText == \"\"")

        healthy = len(issues) == 0
        return {
            "healthy": healthy,
            "issues": issues
        }
