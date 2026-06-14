from typing import Any, Dict, List
from datetime import datetime
import math
from engines.agents.base_agent import BaseAgent
from foundation.shared.events import SimulationCompletedEvent

class SimulatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="SimulatorAgent")

    def execute(self, action: str, payload: Any) -> Any:
        if action == "simulate":
            return self.simulate_outcome(payload)
        else:
            raise ValueError(f"Unknown action {action} for SimulatorAgent")

    def simulate_outcome(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        V2 Simulator Logic:
        * Retrieve mission rules from the graph (RULE# records).
        * Retrieve all required/optional products for the mission.
        * Calculate required quantities based on guest_count and serves_per_unit rules.
        * Compare against cart contents to compute gaps.
        * Derive success_probability from coverage, weighting critical products higher.
        * Generate human-readable assumptions.
        """
        from graph.service import GraphService
        
        graph_service = GraphService()
        
        mission_id = payload.get("mission_id", "")
        guest_count_val = payload.get("guest_count")
        guest_count = int(guest_count_val) if guest_count_val is not None else 1
        cart_products = payload.get("cart_products", [])
        user_id = payload.get("user_id", "")
        
        # Legacy fallback: if payload has old-style fields, handle gracefully
        if not mission_id and "scenario" in payload:
            # Old-style call from orchestrator - return backward-compat result
            scenario = payload.get("scenario", "normal")
            outcome = "success" if scenario != "high_risk" else "failure"
            return {
                "outcome": outcome,
                "details": {
                    "predicted_satisfaction": 0.85 if outcome == "success" else 0.4,
                    "alternative_scenarios": ["safe_checkout", "postponed_checkout"]
                },
                "required_products": {},
                "available_products": {},
                "quantity_gaps": {},
                "success_probability": 85 if outcome == "success" else 40,
                "assumptions": ["Legacy simulation mode — upgrade orchestrator to pass mission_id and cart_products."]
            }
        
        # Build cart availability map
        cart_map = {}
        for cp in cart_products:
            p_name = cp.get("product", "").lower()
            qty = int(cp.get("quantity", 1))
            cart_map[p_name] = cart_map.get(p_name, 0) + qty
        
        # Get consumption rules from graph
        rules = graph_service.get_mission_rules(mission_id)
        rules_map = {}
        for rule in rules:
            rules_map[rule["product"].lower()] = rule["serves_per_unit"]
        
        # Get all required products for the mission
        reqs_weighted = graph_service.get_mission_requirements_weighted(mission_id)
        
        required_products = {}
        available_products = {}
        quantity_gaps = {}
        assumptions = []
        
        total_weight = 0
        covered_weight = 0
        
        for req in reqs_weighted:
            product_id = req["product_id"].lower()
            weight = req["weight"]
            priority = req.get("priority", "IMPORTANT")
            
            # Calculate required quantity
            if product_id in rules_map:
                serves_per_unit = rules_map[product_id]
                required_qty = math.ceil(guest_count / serves_per_unit) if serves_per_unit > 0 else guest_count
                assumptions.append(f"One {product_id.replace('_', ' ')} serves {int(serves_per_unit)} guests.")
            else:
                # Default: 1:1 ratio (one per guest)
                required_qty = guest_count
                assumptions.append(f"{product_id.replace('_', ' ').capitalize()} estimated at 1 per guest.")
            
            required_products[product_id] = required_qty
            available_qty = cart_map.get(product_id, 0)
            
            if available_qty > 0:
                available_products[product_id] = available_qty
            
            gap = max(0, required_qty - available_qty)
            if gap > 0:
                quantity_gaps[product_id] = gap
            
            # Weight-based coverage
            # Priority multiplier: CRITICAL items weigh more in success calculation
            priority_multiplier = 3.0 if priority == "CRITICAL" else (1.5 if priority == "IMPORTANT" else 1.0)
            effective_weight = weight * priority_multiplier
            total_weight += effective_weight
            
            if available_qty >= required_qty:
                covered_weight += effective_weight
            elif available_qty > 0:
                # Partial coverage
                coverage_ratio = available_qty / required_qty
                covered_weight += effective_weight * coverage_ratio
        
        # Calculate success probability
        if total_weight > 0:
            success_probability = int(round((covered_weight / total_weight) * 100))
        else:
            success_probability = 100  # No requirements means full success
        
        success_probability = max(0, min(100, success_probability))
        
        result = {
            "required_products": required_products,
            "available_products": available_products,
            "quantity_gaps": quantity_gaps,
            "success_probability": success_probability,
            "assumptions": assumptions,
        }
        
        # Emit SimulationCompletedEvent
        outcome = "success" if success_probability >= 70 else ("risk" if success_probability >= 40 else "failure")
        event = SimulationCompletedEvent(
            user_id=user_id or "UNKNOWN_USER",
            scenario=f"mission_{mission_id}",
            outcome=outcome,
            details={"success_probability": success_probability, "gaps": len(quantity_gaps)},
            completed_at=datetime.utcnow().isoformat()
        )
        self.emit_event("SimulationCompletedEvent", event.dict())
        
        return result
