from typing import List
from engines.domains.regret_prevention.schemas import RegretPreventionRequest, RegretPreventionResponseData
from foundation.graph.repository import GraphRepository

class RegretPreventionService:
    def __init__(self):
        self.graph_repo = GraphRepository()

    def evaluate(self, data: RegretPreventionRequest) -> RegretPreventionResponseData:
        forgotten_items = []
        impact_score = 0
        
        cart_set = set(data.cart_products)
        
        # 1. Check OPTIONAL mission items
        optional_edges = self.graph_repo.query_by_pk(f"MISSION#{data.mission_id}", "OPTIONAL#")
        for edge in optional_edges:
            target = edge.get("SK", "").split("#")[-1]
            if target and target not in cart_set:
                if target not in forgotten_items:
                    forgotten_items.append(target)
                    impact_score += 5
                    
        # 2. Check DEPENDS_ON and COMPATIBLE_WITH for items already in the cart
        for item in cart_set:
            # DEPENDS_ON
            deps = self.graph_repo.query_by_pk(f"PRODUCT#{item}", "DEPENDS_ON#")
            for dep in deps:
                target = dep.get("SK", "").split("#")[-1]
                if target and target not in cart_set:
                    if target not in forgotten_items:
                        forgotten_items.append(target)
                        impact_score += 15  # Missing a dependency is high impact
                        
            # COMPATIBLE_WITH
            comps = self.graph_repo.query_by_pk(f"PRODUCT#{item}", "COMPATIBLE_WITH#")
            for comp in comps:
                target = comp.get("SK", "").split("#")[-1]
                if target and target not in cart_set:
                    if target not in forgotten_items:
                        forgotten_items.append(target)
                        impact_score += 2  # Compatible items are nice to have
                        
        impact_score = min(100, impact_score)
        
        return RegretPreventionResponseData(
            forgotten_items=forgotten_items,
            impact_score=impact_score
        )
