from engines.domains.verification.repository import VerificationRepository
from engines.domains.verification.schemas import VerificationRequest, VerificationResponseData

from foundation.domains.missions.service import MissionService
from foundation.domains.carts.service import CartService
from foundation.domains.graph.service import GraphService

class VerificationService:
    def __init__(self):
        self.repository = VerificationRepository()
        self.mission_service = MissionService()
        self.cart_service = CartService()
        self.graph_service = GraphService()

    def verify(self, data: VerificationRequest) -> VerificationResponseData:
        """
        Business Logic:
        * Compare mission requirements against cart contents.
        * Calculate verification_score.
        """
        # Fetch from integrated services
        # We ensure mission and cart exist (raises NotFoundException if they don't)
        self.mission_service.get_mission(data.missionId)
        
        # Get requirements from graph
        mission_requirements = self.graph_service.get_mission_requirements(data.missionId)
        
        # Get cart items
        cart_data = self.cart_service.get_cart_with_items(data.cartId)
        cart_items = cart_data.get("items", [])
        # cart_items are CartItemModel instances; we need product_ids
        cart_contents = [item.product_id for item in cart_items]
        
        missing_items = []
        verification_score = 100
        
        if mission_requirements:
            deduction_per_item = 100 / len(mission_requirements)
        else:
            deduction_per_item = 0

        for req in mission_requirements:
            if req not in cart_contents:
                missing_items.append(req)
                verification_score -= deduction_per_item
                
        # Prevent negative score and round
        verification_score = max(0, int(round(verification_score)))
        
        # Calculate readiness_score
        total_required_items = len(mission_requirements)
        if total_required_items > 0:
            required_items_present = total_required_items - len(missing_items)
            readiness_score = int(round((required_items_present / total_required_items) * 100))
        else:
            readiness_score = 100
            
        # Generate recommended additions
        recommended_additions = []
        for missing in missing_items:
            try:
                substitutes = self.graph_service.get_product_substitutes(missing)
                if substitutes:
                    recommended_additions.extend(substitutes)
            except Exception:
                pass
                
        # Deduplicate recommendations
        recommended_additions = list(set(recommended_additions))
            
        return VerificationResponseData(
            verification_score=verification_score,
            missing_items=missing_items,
            readiness_score=readiness_score,
            recommended_additions=recommended_additions
        )
