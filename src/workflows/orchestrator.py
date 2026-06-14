from typing import Any, Dict
from agents.base_agent import BaseAgent
from domains.verification.service import VerificationService
from domains.risk.service import RiskService
from domains.prevention.service import PreventionService
from agents.memory_agent import MemoryAgent
from agents.adaptive_agent import AdaptiveAgent
from agents.simulator_agent import SimulatorAgent
from shared.schemas.engine_schemas import VerificationRequest, RiskRequest, PreventionRequest

class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="OrchestratorAgent")
        self.verification_service = VerificationService()
        self.risk_service = RiskService()
        self.prevention_service = PreventionService()
        self.memory_agent = MemoryAgent()
        self.adaptive_agent = AdaptiveAgent()
        self.simulator_agent = SimulatorAgent()

    def execute(self, action: str, payload: Any) -> Any:
        if action == "run_checkout_workflow":
            return self.run_checkout_workflow(payload)
        else:
            raise ValueError(f"Unknown action {action} for OrchestratorAgent")

    def run_checkout_workflow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        V2 Orchestrator Workflow:
        Coordinates verification, risk analysis, prevention check, outcome simulation,
        and adaptive planning using V2 graph data.
        """
        user_id = payload.get("user_id", "anonymous")
        cart_id = payload.get("cart_id")
        mission_id = payload.get("mission_id", "birthday_party")
        context = payload.get("context", {})
        
        # 1. Adapt rules based on user + mission context
        from graph.service import GraphService
        gs = GraphService()
        metadata = gs.get_mission_metadata(mission_id)
        mission_category = metadata.get("category", "") if metadata else ""
        
        adaptation = self.adaptive_agent.execute("adapt", {
            "user_id": user_id,
            "mission_id": mission_id,
            "mission_category": mission_category,
            "urgency": context.get("urgency", ""),
        })
        
        # 2. Verification check (V2 weighted)
        verification_req = VerificationRequest(missionId=mission_id, cartId=cart_id)
        verification_res = self.verification_service.verify(verification_req)
        
        # 3. Risk check (V2 multi-dimensional)
        risk_req = RiskRequest(
            verification_score=verification_res.verification_score,
            missing_items=verification_res.missing_items,
            mission_id=mission_id,
            cart_id=cart_id,
            user_id=user_id,
            critical_completion=verification_res.critical_completion,
            context=context if context else None,
        )
        risk_res = self.risk_service.analyze(risk_req)
        
        # 4. Prevention check (uses V2 graph dependencies)
        prevention_req = PreventionRequest(cartId=cart_id)
        prevention_res = self.prevention_service.evaluate(prevention_req)
        
        # 5. Outcome simulation (V2 graph-driven)
        cart_products = []
        try:
            from domains.carts.repository import CartRepository
            cart_repo = CartRepository()
            cart_items = cart_repo.get_cart_items(cart_id)
            cart_products = [{"product": ci.product_id, "quantity": int(ci.quantity)} for ci in cart_items]
        except Exception:
            pass
        
        guest_count_val = context.get("guest_count")
        guest_count = int(guest_count_val) if guest_count_val is not None else 1
        sim_res = self.simulator_agent.execute("simulate", {
            "user_id": user_id,
            "mission_id": mission_id,
            "guest_count": guest_count,
            "cart_products": cart_products,
        })
        
        # 6. Store memory of interaction
        self.memory_agent.execute("store", {
            "user_id": user_id,
            "memory_type": "mission_checkout",
            "content": {
                "mission_id": mission_id,
                "mission_name": metadata.get("name", mission_id) if metadata else mission_id,
                "status": "ACTIVE",
            }
        })
        
        return {
            "success": True,
            "data": {
                "user_id": user_id,
                "cart_id": cart_id,
                "mission_id": mission_id,
                "verification": verification_res,
                "risk": risk_res,
                "prevention": prevention_res,
                "simulation": sim_res,
                "adapted_rules": adaptation.get("adapted_rules", {}),
                "shopper_type": adaptation.get("shopper_type", ""),
            }
        }
