from domains.verification.repository import VerificationRepository
from domains.verification.schemas import VerificationRequest, VerificationResponseData

from domains.missions.service import MissionService
from domains.carts.service import CartService
from graph.service import GraphService

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
        
        # Get requirements from graph (weighted V2)
        mission_requirements = self.graph_service.get_mission_requirements_weighted(data.missionId)
        
        # Get cart items
        cart_data = self.cart_service.get_cart_with_items(data.cartId)
        cart_items = cart_data.get("items", [])
        # cart_items are CartItemModel instances; we need product_ids
        cart_contents = [item.product_id for item in cart_items]
        
        missing_items = []
        critical_missing = []
        important_missing = []
        optional_missing = []
        
        total_critical = 0
        total_important = 0
        total_optional = 0
        
        present_critical = 0
        present_important = 0
        present_optional = 0
        
        verification_score = 100
        
        if mission_requirements:
            required_count = sum(1 for req in mission_requirements if req["required"])
            deduction_per_item = 100 / required_count if required_count > 0 else 0
        else:
            deduction_per_item = 0

        for req in mission_requirements:
            pid = req["product_id"]
            priority = req["priority"]
            is_required = req["required"]
            
            # Check if item or its substitutes are in the cart
            substitutes = []
            try:
                substitutes = self.graph_service.get_product_substitutes(pid)
            except Exception:
                pass
                
            is_present = pid in cart_contents or any(sub in cart_contents for sub in substitutes)
            
            if priority == "CRITICAL":
                total_critical += 1
                if is_present: present_critical += 1
                else: critical_missing.append(pid)
            elif priority == "IMPORTANT":
                total_important += 1
                if is_present: present_important += 1
                else: important_missing.append(pid)
            elif priority == "OPTIONAL":
                total_optional += 1
                if is_present: present_optional += 1
                else: optional_missing.append(pid)
                
            if is_required and not is_present:
                missing_items.append(pid)
                verification_score -= deduction_per_item
                
        # Prevent negative score and round
        verification_score = max(0, int(round(verification_score)))
        
        # Calculate readiness_score
        total_required_items = total_critical + total_important
        if total_required_items > 0:
            required_items_present = present_critical + present_important
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
            critical_missing=critical_missing,
            important_missing=important_missing,
            optional_missing=optional_missing,
            critical_completion=(present_critical / total_critical) if total_critical > 0 else 1.0,
            important_completion=(present_important / total_important) if total_important > 0 else 1.0,
            optional_completion=(present_optional / total_optional) if total_optional > 0 else 1.0,
            readiness_score=readiness_score,
            recommended_additions=recommended_additions
        )
