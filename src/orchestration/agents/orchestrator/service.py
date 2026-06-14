from typing import Dict, Any, List
from datetime import datetime

from engines.agents.base_agent import BaseAgent
from engines.agents.mission_agent import MissionAgent
from engines.agents.memory_agent import MemoryAgent
from engines.domains.verification.service import VerificationService
from engines.domains.risk.service import RiskService
from engines.agents.adaptive_agent import AdaptiveAgent
from engines.agents.simulator_agent import SimulatorAgent
from engines.domains.prevention.service import PreventionService
from orchestration.agents.orchestrator.workflow_manager import WorkflowManager
from orchestration.agents.orchestrator.response_builder import ResponseBuilder
from orchestration.agents.orchestrator.schemas import MissionExecutionRequest, MissionExecutionResponse

from foundation.shared.schemas.engine_schemas import VerificationRequest, RiskRequest, PreventionRequest
from foundation.shared.schemas.mission_schemas import MissionCreate, MissionUpdate
from foundation.shared.services.product_service import ProductService
from foundation.graph.service import GraphService

from foundation.shared.events import (
    MissionLoadedEvent,
    VerificationCompletedEvent,
    RiskCalculatedEvent,
    SimulationCompletedEvent,
    CheckoutDecisionEvent
)

class OrchestratorService(BaseAgent):
    def __init__(self):
        super().__init__(name="OrchestratorAgent")
        self.mission_agent = MissionAgent()
        self.memory_agent = MemoryAgent()
        self.verification_service = VerificationService()
        self.risk_service = RiskService()
        self.adaptive_agent = AdaptiveAgent()
        self.simulator_agent = SimulatorAgent()
        self.prevention_service = PreventionService()
        
        self.graph_service = GraphService()
        self.product_service = ProductService()
        
        self.workflow_manager = WorkflowManager()
        self._register_default_workflows()

    def execute(self, action: str, payload: Any) -> Any:
        if action == "execute_mission":
            return self.execute_mission(payload)
        else:
            raise ValueError(f"Unknown action '{action}' for OrchestratorService")

    def execute_mission(self, request: MissionExecutionRequest) -> MissionExecutionResponse:
        """Executes the entire mission pipeline by running the Mission Checkout Workflow."""
        initial_state = {
            "userId": request.userId,
            "missionId": request.missionId,
            "cartId": request.cartId,
            "context": request.context.dict() if request.context else {},
            "recommendations_data": []
        }
        
        # Execute the primary checkout workflow
        final_state = self.workflow_manager.execute_workflow("Mission Checkout Workflow", initial_state)
        
        # Build standard output envelope
        return ResponseBuilder.build_response(final_state)

    def _register_default_workflows(self) -> None:
        """Registers the default required workflows with pluggable steps."""
        
        # 1. Mission Creation Workflow
        self.workflow_manager.register_step("Mission Creation Workflow", self._step_create_mission)
        
        # 2. Mission Validation Workflow
        self.workflow_manager.register_step("Mission Validation Workflow", self._step_load_mission_context)
        self.workflow_manager.register_step("Mission Validation Workflow", self._step_run_verification)
        
        # 3. Mission Checkout Workflow
        self.workflow_manager.register_step("Mission Checkout Workflow", self._step_load_mission_context)
        self.workflow_manager.register_step("Mission Checkout Workflow", self._step_retrieve_memory)
        self.workflow_manager.register_step("Mission Checkout Workflow", self._step_run_verification)
        self.workflow_manager.register_step("Mission Checkout Workflow", self._step_run_risk_analysis)
        self.workflow_manager.register_step("Mission Checkout Workflow", self._step_run_adaptive_logic)
        self.workflow_manager.register_step("Mission Checkout Workflow", self._step_run_outcome_simulation)
        self.workflow_manager.register_step("Mission Checkout Workflow", self._step_run_checkout_prevention)
        self.workflow_manager.register_step("Mission Checkout Workflow", self._step_generate_recommendations)
        
        # 4. Mission Recommendation Workflow
        self.workflow_manager.register_step("Mission Recommendation Workflow", self._step_generate_recommendations)
        
        # 5. Future AI Recommendation Workflow (Placeholder/pluggable)
        self.workflow_manager.register_step("Future AI Recommendation Workflow", lambda state: state)

    # --- Step Implementations ---

    def _step_create_mission(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Wrapper step to create a new mission model."""
        mission_input = state.get("mission_input")
        if mission_input:
            created = self.mission_agent.execute("create", mission_input)
            state["mission_data"] = created.to_dict()
        return state

    def _step_load_mission_context(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Loads mission context and requirements from DynamoDB via MissionAgent."""
        mission_id = state["missionId"]
        
        # Try to load mission from graph metadata first
        metadata = self.graph_service.get_mission_metadata(mission_id)
        if metadata:
            state["mission_data"] = {
                "mission_id": metadata.get("mission_id", mission_id),
                "name": metadata.get("name", f"Mission {mission_id}"),
                "category": metadata.get("category", ""),
                "description": metadata.get("description", ""),
            }
        else:
            # Try MissionAgent
            try:
                mission = self.mission_agent.execute("get", mission_id)
                state["mission_data"] = mission.to_dict()
            except Exception:
                # Treat mission_id as query for semantic detection
                from domains.missions.detection_service import DetectionService
                detector = DetectionService()
                res = detector.detect_mission(mission_id)
                if res.get("success"):
                    detected_id = res["mission_id"]
                    state["missionId"] = detected_id
                    state["detection_data"] = res
                    # Try graph metadata for detected mission
                    detected_meta = self.graph_service.get_mission_metadata(detected_id)
                    if detected_meta:
                        state["mission_data"] = {
                            "mission_id": detected_meta.get("mission_id", detected_id),
                            "name": detected_meta.get("name", f"Mission {detected_id}"),
                            "category": detected_meta.get("category", ""),
                        }
                    else:
                        try:
                            mission = self.mission_agent.execute("get", detected_id)
                            state["mission_data"] = mission.to_dict()
                        except Exception:
                            state["mission_data"] = {"mission_id": detected_id, "name": f"Mission {detected_id}"}
                    mission_id = detected_id
                else:
                    state["mission_data"] = {"mission_id": mission_id, "name": f"Mission {mission_id}"}
            
        # Get requirements from Graph
        requirements = self.graph_service.get_mission_requirements(mission_id)
        state["required_products"] = requirements
        
        # Emit MissionLoadedEvent
        event = MissionLoadedEvent(
            mission_id=mission_id,
            user_id=state["userId"],
            required_products=requirements,
            loaded_at=datetime.utcnow().isoformat()
        )
        self.emit_event("MissionLoadedEvent", event.dict())
        # Store active mission state in Memory Repository/Agent (Phase 11 V2 schema support)
        try:
            from domains.memory.schemas import MissionStateRequest
            from domains.memory.service import MemoryService
            memory_service = MemoryService()
            memory_service.track_mission(MissionStateRequest(
                user_id=state["userId"],
                mission_id=mission_id,
                mission_name=state["mission_data"].get("name", mission_id),
                status="ACTIVE"
            ))
        except Exception:
            pass

        return state

    def _step_retrieve_memory(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves historical interaction context for the user."""
        user_id = state["userId"]
        memory = self.memory_agent.execute("retrieve", {"user_id": user_id, "memory_type": "last_checkout_workflow"})
        
        # Return structured defaults if no memory exists yet
        if not memory:
            memory = {
                "frequentMissions": [state["missionId"]],
                "averageBudget": state.get("context", {}).get("budget", 500.0)
            }
        state["memory_data"] = memory
        return state

    def _step_run_verification(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Compares cart against requirements using V2 weighted priorities."""
        req = VerificationRequest(
            missionId=state["missionId"],
            cartId=state["cartId"]
        )
        res = self.verification_service.verify(req)
        state["verification_data"] = res.dict()
        
        # Emit VerificationCompletedEvent
        event = VerificationCompletedEvent(
            mission_id=state["missionId"],
            cart_id=state["cartId"],
            score=res.verification_score,
            missing_items=res.missing_items,
            completed_at=datetime.utcnow().isoformat()
        )
        self.emit_event("VerificationCompletedEvent", event.dict())

        # Update cart's detected mission and readiness score in DynamoDB (Phase 9 V2 schema support)
        try:
            from domains.carts.repository import CartRepository
            cart_repo = CartRepository()
            cart = cart_repo.get_cart(state["cartId"])
            if cart:
                cart.detected_mission = state["missionId"]
                cart.readiness_score = res.verification_score
                cart_repo.update_cart(cart)
        except Exception:
            pass

        return state

    def _step_run_risk_analysis(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates multi-dimensional risk using V2 graph data."""
        verification = state.get("verification_data", {})
        context = state.get("context", {})
        
        req = RiskRequest(
            verification_score=verification.get("verification_score", 0),
            missing_items=verification.get("missing_items", []),
            mission_id=state["missionId"],
            cart_id=state["cartId"],
            user_id=state["userId"],
            critical_completion=verification.get("critical_completion", 0.0),
            context=context if context else None,
        )
        res = self.risk_service.analyze(req)
        state["risk_data"] = res.dict()
        
        # Emit RiskCalculatedEvent
        event = RiskCalculatedEvent(
            user_id=state["userId"],
            cart_id=state["cartId"],
            score=float(res.risk_score),
            status="risky" if res.risk_score >= 70 else ("suspicious" if res.risk_score >= 30 else "safe"),
            calculated_at=datetime.utcnow().isoformat()
        )
        self.emit_event("RiskCalculatedEvent", event.dict())
        return state

    def _step_run_adaptive_logic(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """V2 Adaptive: determines persona from mission context and user history."""
        user_id = state["userId"]
        context = state.get("context", {})
        mission_data = state.get("mission_data", {})
        
        adaptive_res = self.adaptive_agent.execute("adapt", {
            "user_id": user_id,
            "mission_id": state["missionId"],
            "mission_category": mission_data.get("category", ""),
            "cart_size": len(state.get("required_products", [])),
            "urgency": context.get("urgency", ""),
            "history": [state["missionId"]],
        })
        
        # Inject urgency to strictMode if context demands it
        if context.get("urgency") == "HIGH":
            adaptive_res["adapted_rules"]["strict_mode"] = True
            
        state["adaptive_data"] = adaptive_res
        return state

    def _step_run_outcome_simulation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """V2 Simulation: uses mission rules, guest_count, and cart contents."""
        user_id = state["userId"]
        context = state.get("context", {})
        
        # Build cart products list
        cart_products = []
        try:
            from domains.carts.repository import CartRepository
            cart_repo = CartRepository()
            cart_items = cart_repo.get_cart_items(state["cartId"])
            for ci in cart_items:
                cart_products.append({"product": ci.product_id, "quantity": int(ci.quantity)})
        except Exception:
            pass
        
        guest_count_val = context.get("guest_count")
        guest_count = int(guest_count_val) if guest_count_val is not None else 1
        
        res = self.simulator_agent.execute("simulate", {
            "user_id": user_id,
            "mission_id": state["missionId"],
            "guest_count": guest_count,
            "cart_products": cart_products,
        })
        state["simulation_data"] = res
        
        # Emit SimulationCompletedEvent
        event = SimulationCompletedEvent(
            user_id=user_id,
            scenario=f"mission_{state['missionId']}",
            outcome="success" if res.get("success_probability", 0) >= 70 else "risk",
            details={"success_probability": res.get("success_probability", 0)},
            completed_at=datetime.utcnow().isoformat()
        )
        self.emit_event("SimulationCompletedEvent", event.dict())
        return state

    def _step_run_checkout_prevention(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Determines if checkout can proceed based on V2 verification and risk data."""
        verification = state.get("verification_data", {})
        risk = state.get("risk_data", {})
        adaptive = state.get("adaptive_data", {})
        
        strict_mode = adaptive.get("adapted_rules", {}).get("strict_mode", False)
        
        # V2 Prevention Logic: use actual verification and risk data
        readiness = verification.get("verification_score", 0)
        critical_missing = verification.get("critical_missing", [])
        overall_risk = risk.get("risk_score", 0)
        
        allow_checkout = True
        reason = ""
        
        # Block if critical items are missing
        if critical_missing:
            allow_checkout = False
            reason = f"Missing critical items: {', '.join(c.replace('_', ' ').title() for c in critical_missing)}."
        
        # Block if overall risk is too high
        if overall_risk >= 70:
            allow_checkout = False
            reason = reason or f"Overall risk is too high ({overall_risk}%)."
        
        # Strict mode: block if readiness < 80%
        if strict_mode and readiness < 80:
            allow_checkout = False
            reason = reason or f"Urgent mission strict mode active. Readiness ({readiness}%) must be at least 80%."
        
        state["prevention_data"] = {
            "allow_checkout": allow_checkout,
            "reason": reason,
        }
        
        # Emit CheckoutDecisionEvent
        event = CheckoutDecisionEvent(
            user_id=state["userId"],
            cart_id=state["cartId"],
            allow_checkout=allow_checkout,
            blocking_issues=[reason] if not allow_checkout else [],
            decided_at=datetime.utcnow().isoformat()
        )
        self.emit_event("CheckoutDecisionEvent", event.dict())

        # Track completed mission state in Memory Repository/Agent (Phase 11 V2 schema support)
        if allow_checkout:
            try:
                from domains.memory.schemas import MissionStateRequest
                from domains.memory.service import MemoryService
                memory_service = MemoryService()
                memory_service.track_mission(MissionStateRequest(
                    user_id=state["userId"],
                    mission_id=state["missionId"],
                    mission_name=state["mission_data"].get("name", state["missionId"]),
                    status="COMPLETED"
                ))
            except Exception:
                pass

        return state

    def _step_generate_recommendations(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Finds substitutes for missing cart items via the Knowledge Graph."""
        verification = state.get("verification_data", {})
        missing_items = verification.get("missing_items", [])
        
        recs = []
        for item_name in missing_items:
            # Query graph for potential substitutes
            substitutes = []
            try:
                substitutes = self.graph_service.get_product_substitutes(item_name)
            except Exception:
                pass
                
            sub_name = substitutes[0] if substitutes else f"Premium {item_name.replace('_', ' ').title()}"
            
            recs.append({
                "product_id": f"SUB_{item_name.upper()}",
                "name": sub_name,
                "price": 45.0,
                "reason": f"Required for mission {state['missionId']}. Substitute for missing {item_name.replace('_', ' ')}."
            })
            
        state["recommendations_data"] = recs
        return state
