from engines.domains.prevention.repository import PreventionRepository
from engines.domains.prevention.schemas import PreventionRequest, PreventionResponseData

from engines.domains.verification.service import VerificationService
from engines.domains.verification.schemas import VerificationRequest
from engines.domains.risk.service import RiskService
from engines.domains.risk.schemas import RiskRequest

class PreventionService:
    def __init__(self):
        self.repository = PreventionRepository()
        self.verification_service = VerificationService()
        self.risk_service = RiskService()

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
            reason = "Unable to verify product dependencies."

        return PreventionResponseData(
            allow_checkout=allow_checkout,
            reason=reason
        )
