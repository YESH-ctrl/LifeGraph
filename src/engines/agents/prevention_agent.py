from typing import Any
from datetime import datetime
from engines.agents.base_agent import BaseAgent
from foundation.shared.schemas.engine_schemas import PreventionRequest, PreventionResponseData
from foundation.shared.events import CheckoutBlockedEvent
from foundation.infrastructure.dynamodb.base_repository import BaseRepository

class PreventionRepository(BaseRepository):
    pass

class PreventionAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="PreventionAgent")
        self.repository = PreventionRepository()

    def execute(self, action: str, payload: Any) -> Any:
        if action == "evaluate":
            return self.evaluate(payload)
        else:
            raise ValueError(f"Unknown action {action} for PreventionAgent")

    def evaluate(self, data: PreventionRequest) -> PreventionResponseData:
        """
        V2 Prevention Logic:
        * Check product dependencies from the graph.
        * Block checkout if required dependencies are missing.
        """
        from graph.service import GraphService
        from domains.carts.repository import CartRepository

        graph_service = GraphService()
        allow_checkout = True
        reason = ""

        try:
            cart_repo = CartRepository()
            cart_items = cart_repo.get_cart_items(data.cartId)
            cart_product_ids = [ci.product_id.lower() for ci in cart_items]

            missing_deps = []
            for p_id in cart_product_ids:
                deps = graph_service.get_product_dependencies(p_id)
                for dep in deps:
                    if dep.lower() not in cart_product_ids and dep not in missing_deps:
                        missing_deps.append(dep)

            if missing_deps:
                allow_checkout = False
                reason = f"Missing required dependencies: {', '.join(d.replace('_', ' ').title() for d in missing_deps)}."
        except Exception:
            # If cart cannot be loaded, allow checkout with a warning
            reason = "Unable to verify product dependencies."

        res_data = PreventionResponseData(
            allow_checkout=allow_checkout,
            reason=reason
        )

        # Emit CheckoutBlockedEvent if blocked
        if not allow_checkout:
            event = CheckoutBlockedEvent(
                user_id="UNKNOWN_USER",
                cart_id=data.cartId,
                reason=reason,
                blocked_at=datetime.utcnow().isoformat()
            )
            self.emit_event("CheckoutBlockedEvent", event.dict())

        return res_data
