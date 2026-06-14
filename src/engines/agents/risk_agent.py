from typing import Any, Dict, List
from datetime import datetime
import math
from engines.agents.base_agent import BaseAgent
from foundation.shared.schemas.engine_schemas import RiskRequest, RiskResponseData
from foundation.shared.events import RiskCalculatedEvent
from foundation.infrastructure.dynamodb.base_repository import BaseRepository

class RiskRepository(BaseRepository):
    pass

class RiskAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="RiskAgent")
        self.repository = RiskRepository()

    def execute(self, action: str, payload: Any) -> Any:
        if action == "analyze":
            return self.analyze(payload)
        else:
            raise ValueError(f"Unknown action {action} for RiskAgent")

    def analyze(self, data: RiskRequest) -> RiskResponseData:
        """
        V2 Risk Analysis with 5 independent dimensions:
        1. Completion Risk - derived from critical item gaps
        2. Quantity Risk - derived from mission rules + cart quantities
        3. Compatibility Risk - derived from DEPENDS_ON / COMPATIBLE_WITH relationships
        4. Timing Risk - derived from event date proximity
        5. Budget Risk - derived from budget vs estimated cost
        
        Overall risk = weighted average: completion(40%) + quantity(25%) + compatibility(15%) + timing(10%) + budget(10%)
        """
        from graph.service import GraphService
        from domains.carts.repository import CartRepository

        graph_service = GraphService()

        # --- 1. Completion Risk ---
        # Based on how many critical items are missing
        completion_risk = int(round((1.0 - data.critical_completion) * 100))

        # --- 2. Quantity Risk ---
        quantity_risk = 0
        if data.mission_id:
            rules = graph_service.get_mission_rules(data.mission_id)
            if rules and data.cart_id:
                try:
                    cart_repo = CartRepository()
                    cart_items = cart_repo.get_cart_items(data.cart_id)
                    cart_map = {}
                    for ci in cart_items:
                        cart_map[ci.product_id.lower()] = int(ci.quantity)

                    # Get guest_count from context if available
                    guest_count = 1
                    if data.context:
                        guest_count_val = data.context.get("guest_count")
                        guest_count = int(guest_count_val) if guest_count_val is not None else 1

                    total_products_with_rules = 0
                    products_with_gaps = 0
                    for rule in rules:
                        product = rule["product"].lower()
                        serves_per_unit = rule["serves_per_unit"]
                        required_qty = math.ceil(guest_count / serves_per_unit) if serves_per_unit > 0 else guest_count
                        available_qty = cart_map.get(product, 0)
                        total_products_with_rules += 1
                        if available_qty < required_qty:
                            products_with_gaps += 1

                    if total_products_with_rules > 0:
                        quantity_risk = int(round((products_with_gaps / total_products_with_rules) * 100))
                except Exception:
                    pass

        # --- 3. Compatibility Risk ---
        compatibility_risk = 0
        if data.mission_id and data.cart_id:
            try:
                cart_repo = CartRepository()
                cart_items = cart_repo.get_cart_items(data.cart_id)
                cart_product_ids = [ci.product_id.lower() for ci in cart_items]

                missing_deps_count = 0
                total_deps = 0
                for p_id in cart_product_ids:
                    deps = graph_service.get_product_dependencies(p_id)
                    for dep in deps:
                        total_deps += 1
                        if dep.lower() not in cart_product_ids:
                            missing_deps_count += 1

                if total_deps > 0:
                    compatibility_risk = int(round((missing_deps_count / total_deps) * 100))
            except Exception:
                pass

        # --- 4. Timing Risk ---
        timing_risk = 0
        if data.context and data.context.get("event_date"):
            try:
                from datetime import datetime as dt
                event_date_str = data.context["event_date"]
                event_date = dt.fromisoformat(event_date_str)
                days_remaining = (event_date - dt.utcnow()).days
                if days_remaining <= 0:
                    timing_risk = 100
                elif days_remaining == 1:
                    timing_risk = 80
                elif days_remaining <= 3:
                    timing_risk = 50
                elif days_remaining <= 7:
                    timing_risk = 20
                else:
                    timing_risk = 0
            except Exception:
                pass

        # --- 5. Budget Risk ---
        budget_risk = 0
        if data.context and data.context.get("budget"):
            try:
                budget = float(data.context["budget"])
                # Estimate remaining cost from missing items
                missing_count = len(data.missing_items)
                estimated_cost_per_item = 50.0  # Default estimate per product
                estimated_remaining = missing_count * estimated_cost_per_item
                if budget > 0 and estimated_remaining > budget:
                    budget_risk = min(100, int(round(((estimated_remaining - budget) / budget) * 100)))
            except Exception:
                pass

        # --- Overall Risk (weighted average) ---
        overall_risk = int(round(
            (completion_risk * 0.40) +
            (quantity_risk * 0.25) +
            (compatibility_risk * 0.15) +
            (timing_risk * 0.10) +
            (budget_risk * 0.10)
        ))

        # Backward compat labels
        def risk_label(score):
            if score >= 70:
                return "HIGH"
            elif score >= 30:
                return "MEDIUM"
            return "LOW"

        res_data = RiskResponseData(
            completion_risk=completion_risk,
            quantity_risk=quantity_risk,
            compatibility_risk=compatibility_risk,
            timing_risk=timing_risk,
            budget_risk=budget_risk,
            risk_score=overall_risk,
            compatibility_risk_label=risk_label(compatibility_risk),
            budget_risk_label=risk_label(budget_risk),
            quantity_risk_label=risk_label(quantity_risk),
            timing_risk_label=risk_label(timing_risk),
        )

        # Emit RiskCalculatedEvent
        status = "risky" if overall_risk >= 70 else ("suspicious" if overall_risk >= 30 else "safe")
        event = RiskCalculatedEvent(
            user_id=data.user_id or "UNKNOWN_USER",
            cart_id=data.cart_id or "UNKNOWN_CART",
            score=float(overall_risk),
            status=status,
            calculated_at=datetime.utcnow().isoformat()
        )
        self.emit_event("RiskCalculatedEvent", event.dict())

        return res_data
