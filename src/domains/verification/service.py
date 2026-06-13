from domains.verification.repository import VerificationRepository
from domains.verification.schemas import VerificationRequest, VerificationResponseData

class VerificationService:
    def __init__(self):
        self.repository = VerificationRepository()

    def verify(self, data: VerificationRequest) -> VerificationResponseData:
        """
        Business Logic:
        * Compare mission requirements against cart contents.
        * Calculate verification_score.
        """
        # TODO: Integrate with Mission APIs to get real mission requirements based on data.missionId
        # TODO: Integrate with Graph APIs to understand product relationships
        # TODO: Integrate with Cart APIs to fetch actual cart contents based on data.cartId
        
        # Mock mission requirements for "BIRTHDAY"
        mission_requirements = ["Cake", "Candles", "Drinks", "Snacks"]
        
        # Mock cart contents (in future fetched via Cart API)
        cart_contents = ["Cake", "Balloons", "Drinks"]
        
        missing_items = []
        verification_score = 100
        
        for req in mission_requirements:
            if req not in cart_contents:
                missing_items.append(req)
                verification_score -= 25 # deduct 25 for each missing item
                
        # Prevent negative score
        verification_score = max(0, verification_score)
            
        return VerificationResponseData(
            verification_score=verification_score,
            missing_items=missing_items
        )
