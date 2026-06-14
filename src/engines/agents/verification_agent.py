from typing import Any, List
from datetime import datetime
from engines.agents.base_agent import BaseAgent
from foundation.shared.schemas.engine_schemas import VerificationRequest, VerificationResponseData
from foundation.shared.events import MissionVerifiedEvent
from foundation.infrastructure.dynamodb.base_repository import BaseRepository

class VerificationRepository(BaseRepository):
    pass

class VerificationAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="VerificationAgent")
        self.repository = VerificationRepository()

    def execute(self, action: str, payload: Any) -> Any:
        if action == "verify":
            return self.verify(payload)
        else:
            raise ValueError(f"Unknown action {action} for VerificationAgent")

    def verify(self, data: VerificationRequest) -> VerificationResponseData:
        """
        V2 Verification Logic:
        * Classify mission requirements by priority (CRITICAL, IMPORTANT, OPTIONAL).
        * Calculate per-priority completion rates.
        * Apply weighted readiness formula: CRITICAL=70%, IMPORTANT=20%, OPTIONAL=10%.
        * Return enriched response with priority breakdowns.
        """
        from graph.service import GraphService
        from domains.carts.repository import CartRepository
        
        graph_service = GraphService()
        cart_repository = CartRepository()
        
        reqs_weighted = graph_service.get_mission_requirements_weighted(data.missionId)
        cart_items = cart_repository.get_cart_items(data.cartId)
        cart_contents = [item.product_id.lower() for item in cart_items]

        # Classify requirements by priority
        critical_items = []
        important_items = []
        optional_items = []

        for item in reqs_weighted:
            priority = item.get("priority", "IMPORTANT").upper()
            if priority == "CRITICAL":
                critical_items.append(item)
            elif priority == "OPTIONAL":
                optional_items.append(item)
            else:
                important_items.append(item)

        # Calculate completion for each priority class
        def calc_completion(items_list):
            if not items_list:
                return 1.0, []  # No items means 100% complete, no missing
            total_weight = sum(i["weight"] for i in items_list)
            present_weight = 0
            missing = []
            for i in items_list:
                if i["product_id"].lower() in cart_contents:
                    present_weight += i["weight"]
                else:
                    missing.append(i["product_id"])
            completion = present_weight / total_weight if total_weight > 0 else 1.0
            return completion, missing

        critical_completion, critical_missing = calc_completion(critical_items)
        important_completion, important_missing = calc_completion(important_items)
        optional_completion, optional_missing = calc_completion(optional_items)

        # Weighted readiness score
        readiness_score = (
            (critical_completion * 0.70) +
            (important_completion * 0.20) +
            (optional_completion * 0.10)
        ) * 100
        readiness_score = int(round(readiness_score))

        # All missing items (backward compat)
        all_missing = critical_missing + important_missing + optional_missing

        # Recommended products: critical first, then important
        recommended_products = critical_missing + important_missing

        res_data = VerificationResponseData(
            verification_score=readiness_score,
            missing_items=all_missing,
            critical_completion=round(critical_completion, 2),
            important_completion=round(important_completion, 2),
            optional_completion=round(optional_completion, 2),
            critical_missing=critical_missing,
            important_missing=important_missing,
            optional_missing=optional_missing,
            recommended_products=recommended_products,
        )

        # Emit MissionVerifiedEvent
        event = MissionVerifiedEvent(
            mission_id=data.missionId,
            user_id="UNKNOWN_USER",  # Placeholder since request only contains missionId and cartId
            status="VERIFIED" if readiness_score >= 70 else "FAILED",
            verified_at=datetime.utcnow().isoformat()
        )
        self.emit_event("MissionVerifiedEvent", event.dict())
        
        return res_data

    def get_mission_requirements(self, mission_id: str) -> list:
        """Diagnostic helper returning weighted mission requirements from GraphService.
        Used by audit scripts to verify the VerificationAgent consumes V2 data.
        """
        from graph.service import GraphService
        service = GraphService()
        return service.get_mission_requirements_weighted(mission_id)
