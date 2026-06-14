import math
import re
from typing import Dict, List, Any

from foundation.graph.repository import GraphRepository
from .schemas import CartGenerationRequest, CartGenerationResponse, CartProduct, Substitution

class CartGenerationService:
    def __init__(self):
        self.graph_repo = GraphRepository()

    def generate_cart(self, request: CartGenerationRequest) -> CartGenerationResponse:
        mission_id = request.mission_id
        params = request.parameters
        
        guest_count = params.get("guest_count")
        if not guest_count:
            guest_count = params.get("family_size", 1)
            
        required_items = self.graph_repo.query_by_pk(f"MISSION#{mission_id}", "REQUIRES#")
        optional_items = self.graph_repo.query_by_pk(f"MISSION#{mission_id}", "OPTIONAL#")
        
        required_products = []
        optional_products = []
        substitutions = []
        
        total_cost = 0.0
        reasoning = []
        
        # A helper to process a product node
        def process_product(product_id: str, is_required: bool, priority: str, parent_quantity: int = None, parent_name: str = None):
            nonlocal total_cost
            
            # Metadata
            meta = self.graph_repo.get_item(f"PRODUCT#{product_id}", "METADATA") or {}
            title = meta.get("title", product_id.replace("_", " ").title())
            price = float(meta.get("price", 0.0))
            
            # Serves
            serves_edges = self.graph_repo.query_by_pk(f"PRODUCT#{product_id}", "SERVES#")
            serves_per_unit = 1
            for edge in serves_edges:
                sk = edge.get("SK", "")
                parts = sk.split("#")
                if len(parts) >= 3:
                    quantity_str = parts[2]
                    match = re.search(r'(\d+)', quantity_str)
                    if match:
                        serves_per_unit = max(1, int(match.group(1)))
            
            # Calculate quantity
            if parent_quantity is not None:
                quantity = parent_quantity
            else:
                quantity = math.ceil(guest_count / serves_per_unit)
                if quantity > 1 and serves_per_unit > 1:
                    reasoning.append(f"{title} quantity increased to {quantity} because one unit serves {serves_per_unit} guests.")
            
            cost = price * quantity
            total_cost += cost
            
            cart_prod = CartProduct(
                product_id=product_id,
                title=title,
                quantity=quantity,
                priority=priority,
                estimated_cost=cost
            )
            
            if is_required:
                required_products.append(cart_prod)
            else:
                optional_products.append(cart_prod)
                
            # DEPENDS_ON
            depends = self.graph_repo.query_by_pk(f"PRODUCT#{product_id}", "DEPENDS_ON#")
            for dep in depends:
                sk = dep.get("SK", "")
                parts = sk.split("#")
                if len(parts) >= 3:
                    dep_id = parts[2]
                    # recursively process dependencies as required items that inherit quantity
                    process_product(dep_id, True, "DEPENDENCY", quantity, title)
                    
            # SUBSTITUTES_FOR
            subs = self.graph_repo.query_by_pk(f"PRODUCT#{product_id}", "SUBSTITUTES_FOR#")
            if subs:
                alt_ids = [s.get("SK", "").split("#")[2] for s in subs if len(s.get("SK", "").split("#")) >= 3]
                alt_titles = []
                for alt_id in alt_ids:
                    ameta = self.graph_repo.get_item(f"PRODUCT#{alt_id}", "METADATA") or {}
                    alt_titles.append(ameta.get("title", alt_id.replace("_", " ").title()))
                
                substitutions.append(Substitution(
                    product=title,
                    alternatives=alt_titles
                ))

        # Process Requires
        for item in required_items:
            sk = item.get("SK", "")
            parts = sk.split("#")
            if len(parts) >= 3:
                process_product(parts[2], True, item.get("priority", "CRITICAL"))

        # Process Optional
        for item in optional_items:
            sk = item.get("SK", "")
            parts = sk.split("#")
            if len(parts) >= 3:
                process_product(parts[2], False, item.get("priority", "OPTIONAL"))
                
        # Calculate coverage (simplistic check if required products > 0)
        graph_coverage = 100 if len(required_products) > 0 else 0
        
        return CartGenerationResponse(
            mission_id=mission_id,
            required_products=required_products,
            optional_products=optional_products,
            estimated_total_cost=total_cost,
            estimated_serving_capacity=guest_count,
            graph_coverage=graph_coverage,
            reasoning=reasoning,
            substitutions=substitutions
        )
