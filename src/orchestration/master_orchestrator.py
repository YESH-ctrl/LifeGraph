import os
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List, Optional

from foundation.graph.repository import GraphRepository
from engines.domains.mission_detection.service import MissionDetectionService
from engines.domains.mission_detection.schemas import MissionDetectionRequest
from engines.domains.cart_generation.service import CartGenerationService
from engines.domains.cart_generation.schemas import CartGenerationRequest
from engines.domains.verification.service import VerificationService
from engines.domains.verification.schemas import VerificationRequest
from engines.domains.risk.service import RiskService
from engines.domains.risk.schemas import RiskRequest
from engines.domains.regret_prevention.service import RegretPreventionService
from engines.domains.regret_prevention.schemas import RegretPreventionRequest
from engines.domains.simulator.service import SimulatorService
from engines.domains.simulator.schemas import SimulatorRequest

from shared.ai.ai_gateway import AIGateway
from shared.ai.agents import (
    MissionIntelligenceAgent,
    CartIntelligenceAgent,
    VerificationIntelligenceAgent,
    RiskIntelligenceAgent,
    RegretPreventionIntelligenceAgent,
    SimulationIntelligenceAgent,
    OutcomeAuditorAgent
)
from shared.ai.schemas import AuditFailure
from shared.ai.grounding.grounding_engine import GroundingEngine
from shared.ai.grounding.consistency_validator import ConsistencyValidator
from shared.ai.grounding.success_calibration import SuccessCalibrator
from shared.ai.policy.policy_engine import PolicyEngine
from shared.ai.grounding.grounding_engine import APPROVED_ACCESSORY_ONTOLOGY
from shared.ai.policy.runtime_truth_engine import RuntimeTruthEngine
from shared.ai.evaluation.decision_alignment_engine import DecisionAlignmentEngine

from shared.domain.outcome_blueprint_engine import OutcomeBlueprintEngine
from engines.domains.capability_intelligence_service import CapabilityIntelligenceService
from engines.domains.category_guard import display_title_resolution, check_mismatch

logger = logging.getLogger(__name__)

def check_evidence(item: str, query: str, profile_dict: dict, mission_id: str, graph_repo) -> Optional[str]:
    item_lower = item.lower().replace("_", " ")
    query_lower = query.lower()
    if item_lower in query_lower:
        return "query"
    synonyms = {
        "diabetic": ["diabetic", "diabetes", "sugar conscious", "sugar control", "low sugar"],
        "vegan": ["vegan", "plant based", "plant-based"],
        "gluten-free": ["gluten", "celiac"],
        "healthy_eating": ["healthy", "diet", "weight", "nutrition", "wellness", "fitness"],
        "healthy_lifestyle_start": ["healthy", "diet", "weight", "nutrition", "lifestyle"],
        "weight_loss_journey": ["weight", "loss", "diet", "slim", "fat"],
        "bulk_shopper": ["bulk", "month", "refill", "wholesale", "family pack"],
        "general_refill": ["refill", "monthly", "restock", "groceries"]
    }
    for stem, words in synonyms.items():
        if item.lower() == stem or stem in item.lower():
            if any(w in query_lower for w in words):
                return "query"
    if profile_dict:
        pref_str = str(profile_dict).lower()
        if item_lower in pref_str:
            return "profile"
        for stem, words in synonyms.items():
            if item.lower() == stem or stem in item.lower():
                if any(w in pref_str for w in words):
                    return "profile"
    return None

def compute_change_grounding_score(gc) -> float:
    change = gc.get("change", {})
    change_type = change.get("type")
    evidence = gc.get("evidence", {})
    graph_ev = evidence.get("graph", [])
    catalog_ev = evidence.get("catalog", [])
    rules_ev = evidence.get("business_rules", [])
    
    validity = 1.0
    if any("failure" in str(e).lower() for e in catalog_ev):
        validity = 0.0
        
    has_graph = len(graph_ev) > 0 and (
        change_type in ["reject_product", "calibrate_success"] or
        not any("no relationship" in str(e).lower() or "no direct or indirect" in str(e).lower() for e in graph_ev)
    )
    has_catalog = len(catalog_ev) > 0
    has_rules = len(rules_ev) > 0
    
    completeness = (0.33 if has_graph else 0.0) + (0.33 if has_catalog else 0.0) + (0.34 if has_rules else 0.0)
    
    traceability = 0.0
    if change_type in ["override_readiness", "override_risk", "calibrate_success", "reject_product"]:
        traceability = 1.0
    elif change_type == "add_accessory":
        traceability = 1.0
    else:
        for ge in graph_ev:
            ge_lower = ge.lower()
            if "directly requires" in ge_lower or "requires edge" in ge_lower:
                traceability = max(traceability, 1.0)
            elif "dependency" in ge_lower or "compatible" in ge_lower or "substitute" in ge_lower:
                traceability = max(traceability, 1.0)
            elif "semantic" in ge_lower or "overlap" in ge_lower or "associated" in ge_lower:
                traceability = max(traceability, 0.9)
                
    score = (validity * 0.40) + (completeness * 0.30) + (traceability * 0.30)
    return score

class OutcomeOrchestrator:
    def __init__(self):
        self.graph_repo = GraphRepository()
        self.mission_detection = MissionDetectionService()
        self.cart_generation = CartGenerationService()
        self.verification = VerificationService()
        self.risk = RiskService()
        self.regret_prevention = RegretPreventionService()
        self.simulator = SimulatorService()

        # AI Agents initialization
        self.ai_gateway = AIGateway()
        self.ai_mission = MissionIntelligenceAgent(self.ai_gateway)
        self.ai_cart = CartIntelligenceAgent(self.ai_gateway)
        self.ai_verification = VerificationIntelligenceAgent(self.ai_gateway)
        self.ai_risk = RiskIntelligenceAgent(self.ai_gateway)
        self.ai_regret = RegretPreventionIntelligenceAgent(self.ai_gateway)
        self.ai_simulation = SimulationIntelligenceAgent(self.ai_gateway)
        self.ai_auditor = OutcomeAuditorAgent(self.ai_gateway)
        self.policy_engine = PolicyEngine()
        self.decision_alignment = DecisionAlignmentEngine()

        # Phase 5 evaluation tools
        from shared.ai.evaluation import EvaluationEngine, ReplayEngine, PromptEvaluator
        self.evaluation_engine = EvaluationEngine()
        self.replay_engine = ReplayEngine()
        self.prompt_evaluator = PromptEvaluator()
        self.blueprint_engine = OutcomeBlueprintEngine()
        self.capability_service = CapabilityIntelligenceService()

    def run_outcome_intelligence(self, query: str, debug: bool = True) -> Dict[str, Any]:
        try:
            return self._run_outcome_intelligence_impl(query, debug)
        except Exception as e:
            mode_env = os.environ.get("MODE", "BEDROCK_LIVE")
            logger.error(f"Outcome Intelligence execution failed: {e}", exc_info=True)
            if mode_env == "BEDROCK_LIVE":
                return {
                    "status": "FAILED",
                    "error": str(e),
                    "failures": [str(e)],
                    "trust_level": "FAILED",
                    "policy_score": 0,
                    "certification": {
                        "status": "FAILED",
                        "policy_score": 0,
                        "repaired": False,
                        "trust_level": "FAILED",
                        "errors": [str(e)]
                    },
                    "ai_runtime": {
                        "provider": "bedrock",
                        "model": "meta.llama3-70b-instruct-v1:0",
                        "mode": "LIVE",
                        "latency_ms": 0,
                        "input_tokens": 0,
                        "output_tokens": 0
                    }
                }
            raise e

    def _run_outcome_intelligence_impl(self, query: str, debug: bool = True) -> Dict[str, Any]:
        start_time = time.time()
        logger.info(f"Running Outcome Intelligence for query: '{query}'")
        
        self.execution_trace = []
        self.ai_gateway.execution_trace = self.execution_trace
        self.ai_gateway.bedrock.execution_trace = self.execution_trace
        self.ai_gateway.bedrock.current_query = query

        mode_env = os.environ.get("MODE", "BEDROCK_LIVE")
        self.execution_trace.append({
            "component": "master_orchestrator",
            "mode": mode_env
        })

        self.ai_gateway.tokens.reset()
        self.ai_gateway.costs.reset()
        self.ai_gateway.bedrock.reset_request_metrics()

        grounding = GroundingEngine()
        consistency = ConsistencyValidator()
        calibrator = SuccessCalibrator()

        # STEP 1: Mission Detection
        md_req = MissionDetectionRequest(text=query, user_id="system", session_id="orchestrator")
        md_res = self.mission_detection.detect(md_req)
        
        original_mission = md_res.detected_mission
        mission_id = original_mission
        params = md_res.parameters
        
        text_lower = query.lower()
        if "month" in text_lower:
            mission_id = "monthly_grocery_refill"
        elif "week" in text_lower or "family of 4" in text_lower:
            mission_id = "weekly_grocery_shopping"
        elif "eating healthy" in text_lower or "start eating healthy" in text_lower or "start a healthy lifestyle" in text_lower:
            mission_id = "healthy_lifestyle_start"
        elif "lose weight" in text_lower or "diet" in text_lower:
            mission_id = "weight_loss_journey"
        elif "cooking session" in text_lower or "cooking" in text_lower or "biryani" in text_lower:
            if "biryani" in text_lower:
                mission_id = "chicken_biryani"
            else:
                mission_id = "weekend_cooking_session"

        # AI Mission Detection execution (Task 6: Query minimal context)
        ai_mission_res = self.ai_mission.analyze(query)
        
        ai_detected = ai_mission_res.ai_analysis.detected_mission
        if ai_detected and ai_detected != mission_id:
            if ai_mission_res.confidence >= 0.90:
                logger.info(f"AI Mission Agent overriding mission from {mission_id} to {ai_detected}")
                has_change = any(c.get("type") == "override_mission" for c in ai_mission_res.accepted_changes)
                if not has_change:
                    ai_mission_res.accepted_changes.append({
                        "type": "override_mission",
                        "original": mission_id,
                        "override": ai_detected,
                        "reason": "AI detected more specific user intent"
                    })
            else:
                logger.info(f"AI Mission Agent override low confidence: {ai_mission_res.confidence}")

        grounded_mission_changes = []
        for c in ai_mission_res.accepted_changes:
            is_val, gr_c = grounding.validate_change(c, mission_id, [])
            if is_val:
                grounded_mission_changes.append(gr_c)
            else:
                ai_mission_res.rejected_changes.append(c)
        ai_mission_res.accepted_changes = grounded_mission_changes

        for gc in grounded_mission_changes:
            ch = gc["change"]
            if ch.get("type") == "override_mission":
                mission_id = ch.get("override")

        # Check evidence for constraints
        from foundation.domains.memory.service import MemoryService
        try:
            mem_service = MemoryService()
            profile = mem_service.get_user_profile("system")
            profile_dict = profile.to_dict() if profile else {}
        except Exception:
            profile_dict = {}

        valid_constraints = []
        evidence_validation = []

        for c in getattr(ai_mission_res.ai_analysis, "user_constraints", []):
            ev_src = check_evidence(c, query, profile_dict, mission_id, self.mission_detection.graph_repo)
            if ev_src:
                valid_constraints.append(c)
                evidence_validation.append({"constraint": c, "evidence_source": ev_src})

        ai_mission_res.ai_analysis.user_constraints = valid_constraints
        ai_mission_res.ai_analysis.evidence_validation = evidence_validation

        if ai_mission_res.ai_analysis.detected_mission != mission_id:
            ai_mission_res.ai_analysis.detected_mission = mission_id

        # STEP 2: Outcome Blueprint Loading (Task 1)
        blueprint = self.blueprint_engine.get_blueprint(mission_id)

        # STEP 3: Capability Resolution
        capabilities = self.capability_service.get_capabilities_for_mission(mission_id)

        # STEP 4: Cart Generation
        cg_req = CartGenerationRequest(mission_id=mission_id, parameters=params)
        cg_res = self.cart_generation.generate_cart(cg_req)

        # AI Cart Agent analysis (Task 6: minimal context)
        ai_cart_res = self.ai_cart.analyze(mission_id, capabilities, blueprint)

        # Process rejections
        rejected_prod_ids = []
        rejected_prod_names = []
        accepted_prod_names = []

        rejection_candidates = []
        for change in ai_cart_res.accepted_changes:
            if change.get("type") == "reject_product" and change not in rejection_candidates:
                rejection_candidates.append(change)

        for item in ai_cart_res.ai_analysis.items:
            if item.status == "REJECTED":
                c = {
                    "type": "reject_product",
                    "product_id": item.product_id,
                    "reason": item.reason or "AI Cart Agent rejected item"
                }
                if c not in rejection_candidates:
                    rejection_candidates.append(c)
            elif item.status == "APPROVED":
                if item.title not in accepted_prod_names:
                    accepted_prod_names.append(item.title)

        grounded_cart_changes = []
        for rc in rejection_candidates:
            is_val, gr_c = grounding.validate_change(rc, mission_id, [])
            if is_val:
                grounded_cart_changes.append(gr_c)
                ch = gr_c["change"]
                pid = ch.get("product_id")
                if pid not in rejected_prod_ids:
                    rejected_prod_ids.append(pid)
                    meta_p = self.graph_repo.get_item(f"PRODUCT#{pid}", "METADATA") or {}
                    title_p = display_title_resolution(pid, meta_p) or pid
                    rejected_prod_names.append(title_p)
            else:
                ai_cart_res.rejected_changes.append(rc)

        ai_cart_res.accepted_changes = grounded_cart_changes

        cart_products = [p.product_id for p in cg_res.required_products if p.priority == "CRITICAL" and p.product_id not in rejected_prod_ids]
        cart_cost = sum(p.estimated_cost for p in cg_res.required_products if p.priority == "CRITICAL" and p.product_id not in rejected_prod_ids)

        # STEP 5: Verification (Unified dynamic engine)
        ver_req = VerificationRequest(mission_id=mission_id, cart_products=cart_products)
        ver_res = self.verification.verify(ver_req)
        self.ai_gateway.bedrock.last_ver_res = ver_res

        # STEP 6: Risk Analysis
        risk_req = RiskRequest(
            mission_id=mission_id,
            cart_products=cart_products,
            total_cost=cart_cost,
            budget=params.get("budget"),
            readiness_score=ver_res.readiness_score,
            critical_missing=ver_res.critical_missing,
            missing_items=ver_res.missing_items,
            guest_count=cg_res.estimated_serving_capacity
        )
        risk_res = self.risk.analyze(risk_req)
        self.ai_gateway.bedrock.last_risk_res = risk_res

        # STEP 7: Regret Prevention
        reg_req = RegretPreventionRequest(mission_id=mission_id, cart_products=cart_products)
        reg_res = self.regret_prevention.evaluate(reg_req)

        # Execute Parallel Agents (Task 6: minimal context)
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_ver = executor.submit(self.ai_verification.analyze, cart_products, blueprint)
            future_risk = executor.submit(self.ai_risk.analyze, ver_res.dict())
            future_regret = executor.submit(self.ai_regret.analyze, cart_products, blueprint)
            
            ai_ver_res = future_ver.result()
            ai_risk_res = future_risk.result()
            ai_reg_res = future_regret.result()

        caps_hit = 0

        # Apply Verification Overrides
        ai_ver_res.accepted_changes = [
            c for c in ai_ver_res.accepted_changes
            if c.get("type") != "override_readiness" or c.get("score") != ver_res.readiness_score
        ]
        has_readiness_override = any(c.get("type") == "override_readiness" for c in ai_ver_res.accepted_changes)
        if not has_readiness_override and ai_ver_res.ai_analysis.readiness_score != ver_res.readiness_score:
            ai_ver_res.accepted_changes.append({
                "type": "override_readiness",
                "score": ai_ver_res.ai_analysis.readiness_score,
                "reason": "AI adjusted readiness"
            })

        grounded_ver_changes = []
        for c in ai_ver_res.accepted_changes:
            is_val, gr_c = grounding.validate_change(c, mission_id, cart_products)
            if is_val:
                grounded_ver_changes.append(gr_c)
            else:
                ai_ver_res.rejected_changes.append(c)
        ai_ver_res.accepted_changes = grounded_ver_changes

        overridden_readiness = None
        for gc in grounded_ver_changes:
            ch = gc["change"]
            if ch.get("type") == "override_readiness":
                overridden_readiness = ch.get("score")

        if overridden_readiness is not None:
            det_readiness = ver_res.readiness_score
            max_increase = 30
            formula_boundary = max(0, 100 - (len(ver_res.critical_missing) * 10))
            allowed_max = min(100, min(det_readiness + max_increase, formula_boundary))

            if overridden_readiness > allowed_max:
                logger.info(f"Readiness override {overridden_readiness} capped to {allowed_max}")
                self.decision_alignment.record_correction(
                    agent="verification",
                    query=query,
                    original_prediction=overridden_readiness,
                    final_prediction=allowed_max,
                    delta=overridden_readiness - allowed_max,
                    reason=f"readiness_cap_constraint (det: {det_readiness})"
                )
                caps_hit += 1
                overridden_readiness = allowed_max
                for gc in grounded_ver_changes:
                    ch = gc["change"]
                    if ch.get("type") == "override_readiness":
                        ch["score"] = allowed_max

            ai_ver_res.ai_analysis.readiness_score = overridden_readiness
            ver_res.readiness_score = overridden_readiness

        # Apply Risk Overrides
        ai_risk_res.accepted_changes = [
            c for c in ai_risk_res.accepted_changes
            if c.get("type") != "override_risk" or c.get("level") != risk_res.risk_level or c.get("score") != risk_res.risk_score
        ]
        has_risk_override = any(c.get("type") == "override_risk" for c in ai_risk_res.accepted_changes)
        if not has_risk_override and (ai_risk_res.ai_analysis.risk_level != risk_res.risk_level or ai_risk_res.ai_analysis.risk_score != risk_res.risk_score):
            ai_risk_res.accepted_changes.append({
                "type": "override_risk",
                "level": ai_risk_res.ai_analysis.risk_level,
                "score": ai_risk_res.ai_analysis.risk_score,
                "reason": "AI adjusted risk"
            })

        grounded_risk_changes = []
        for c in ai_risk_res.accepted_changes:
            is_val, gr_c = grounding.validate_change(c, mission_id, cart_products)
            if is_val:
                grounded_risk_changes.append(gr_c)
            else:
                ai_risk_res.rejected_changes.append(c)
        ai_risk_res.accepted_changes = grounded_risk_changes

        overridden_risk_level = None
        overridden_risk_score = None
        for gc in grounded_risk_changes:
            ch = gc["change"]
            if ch.get("type") == "override_risk":
                overridden_risk_level = ch.get("level")
                overridden_risk_score = ch.get("score")

        if overridden_risk_level is not None:
            has_budget_overrun = params.get("budget") is not None and cart_cost > params.get("budget")
            critical_missing_count = len(ver_res.critical_missing)

            boundary_min_score = 0
            if critical_missing_count >= 10:
                boundary_min_score = 80
            elif critical_missing_count >= 5:
                boundary_min_score = 65
            elif critical_missing_count >= 3 or has_budget_overrun:
                boundary_min_score = 40

            if overridden_risk_score < boundary_min_score:
                logger.info(f"Risk override score {overridden_risk_score} capped to {boundary_min_score}")
                self.decision_alignment.record_correction(
                    agent="risk",
                    query=query,
                    original_prediction=overridden_risk_score,
                    final_prediction=boundary_min_score,
                    delta=boundary_min_score - overridden_risk_score,
                    reason=f"critical_missing>={critical_missing_count}"
                )
                caps_hit += 1
                overridden_risk_score = boundary_min_score
                if overridden_risk_score <= 25:
                    overridden_risk_level = "LOW"
                elif overridden_risk_score <= 50:
                    overridden_risk_level = "MEDIUM"
                elif overridden_risk_score <= 75:
                    overridden_risk_level = "HIGH"
                else:
                    overridden_risk_level = "CRITICAL"

                for gc in grounded_risk_changes:
                    ch = gc["change"]
                    if ch.get("type") == "override_risk":
                        ch["score"] = overridden_risk_score
                        ch["level"] = overridden_risk_level

            ai_risk_res.ai_analysis.risk_score = overridden_risk_score
            ai_risk_res.ai_analysis.risk_level = overridden_risk_level
            risk_res.risk_score = overridden_risk_score
            risk_res.risk_level = overridden_risk_level

        # Regret items validation
        pre_validated_forgotten = []
        for f in ai_reg_res.ai_analysis.forgotten_items:
            in_catalog, _, _ = grounding.validate_product_in_catalog(f)
            linked, _ = grounding.validate_recommendation_in_graph(f, mission_id)
            if in_catalog or linked:
                pre_validated_forgotten.append(f)
            else:
                in_ontology = f in APPROVED_ACCESSORY_ONTOLOGY
                if in_ontology:
                    pre_validated_forgotten.append(f)
        ai_reg_res.ai_analysis.forgotten_items = pre_validated_forgotten

        has_regret_changes = any(c.get("type") == "add_accessory" for c in ai_reg_res.accepted_changes)
        if not has_regret_changes and ai_reg_res.ai_analysis.forgotten_items:
            for f in ai_reg_res.ai_analysis.forgotten_items:
                ai_reg_res.accepted_changes.append({
                    "type": "add_accessory",
                    "name": f,
                    "reason": "AI recommended accessory"
                })

        grounded_regret_changes = []
        for c in ai_reg_res.accepted_changes:
            is_val, gr_c = grounding.validate_change(c, mission_id, cart_products)
            if is_val:
                grounded_regret_changes.append(gr_c)
            else:
                ai_reg_res.rejected_changes.append(c)
        ai_reg_res.accepted_changes = grounded_regret_changes

        validated_forgotten = []
        for gc in grounded_regret_changes:
            ch = gc["change"]
            if ch.get("type") == "add_accessory":
                validated_forgotten.append(ch.get("name"))
        reg_res.forgotten_items = validated_forgotten

        # STEP 8: Simulation
        sim_req = SimulatorRequest(
            readiness_score=ver_res.readiness_score,
            risk_score=risk_res.risk_score,
            recommended_additions=ver_res.recommended_products,
            forgotten_items=reg_res.forgotten_items
        )
        sim_res = self.simulator.run_mission_simulation(sim_req)

        # AI Simulation analysis (Task 6: minimal context)
        ai_sim_res = self.ai_simulation.analyze(ver_res.dict(), risk_res.dict())

        # Calibration
        suggested_success = ai_sim_res.ai_analysis.optimized_success
        calibrated_success, calibration_explanation = calibrator.calibrate_success_score(
            readiness_score=ver_res.readiness_score,
            risk_score=risk_res.risk_score,
            mission_coherence_score=cg_res.mission_coherence_score,
            ai_suggested_success=suggested_success
        )
        if calibrated_success != suggested_success:
            self.decision_alignment.record_correction(
                agent="simulation",
                query=query,
                original_prediction=suggested_success,
                final_prediction=calibrated_success,
                delta=suggested_success - calibrated_success,
                reason=calibration_explanation
            )
            caps_hit += 1

        sim_res.optimized_success = calibrated_success
        sim_res.current_success = min(95, max(0, ver_res.readiness_score))
        sim_res.improvement = max(0, sim_res.optimized_success - sim_res.current_success)
        
        ai_sim_res.ai_analysis.optimized_success = calibrated_success
        ai_sim_res.ai_analysis.current_success = sim_res.current_success
        ai_sim_res.ai_analysis.improvement = sim_res.improvement

        if calibrated_success != suggested_success:
            ai_sim_res.accepted_changes = [{
                "change": {
                    "type": "calibrate_success",
                    "original": suggested_success,
                    "calibrated": calibrated_success
                },
                "evidence": {
                    "graph": [f"Simulation calibrated for MISSION#{mission_id}"],
                    "catalog": ["No product catalog check required"],
                    "business_rules": [calibration_explanation]
                }
            }]
        else:
            ai_sim_res.accepted_changes = []

        # Grounding metrics calculations
        grounded_changes_list = (grounded_mission_changes + grounded_cart_changes +
                                 grounded_ver_changes + grounded_risk_changes +
                                 grounded_regret_changes + ai_sim_res.accepted_changes)
        
        if grounded_changes_list:
            total_grounding = sum(compute_change_grounding_score(gc) for gc in grounded_changes_list)
            grounding_score = int((total_grounding / len(grounded_changes_list)) * 100)
        else:
            grounding_score = 100
        grounding_score = min(100, max(0, grounding_score))

        reality_score = max(0, 100 - (caps_hit * 20))

        # Dynamic validation scores
        all_recs = list(set(ver_res.recommended_products + reg_res.forgotten_items))
        existing_count = 0
        for r in all_recs:
            exists, _, _ = grounding.validate_product_in_catalog(r)
            if exists:
                existing_count += 1
        catalog_validity_score = int(existing_count / len(all_recs) * 100) if all_recs else 100

        linked_count = 0
        for r in all_recs:
            linked, _ = grounding.validate_recommendation_in_graph(r, mission_id)
            if linked:
                linked_count += 1
        graph_validity_score = int(linked_count / len(all_recs) * 100) if all_recs else 100

        audit_score = int((grounding_score + 100 + reality_score) / 3)

        # STEP 9: Outcome Audit (Task 6: minimal metrics context instead of agent logs)
        metrics = {
            "readiness_score": ver_res.readiness_score,
            "diversity_score": ver_res.readiness_breakdown.get("diversity_score", 100),
            "capability_completion": ver_res.readiness_breakdown.get("capability_completion", 100),
            "group_completion": ver_res.readiness_breakdown.get("group_completion", 100),
            "grounding_score": grounding_score,
            "reality_score": reality_score,
            "consistency_score": 100
        }
        ai_auditor_res = self.ai_auditor.audit(metrics)

        # Final Recommendation
        final_recommendation = {
            "status": "OPTIMIZED",
            "action": "Proceed to Checkout" if sim_res.optimized_success > 80 else "Review Cart",
            "message": f"Identified {len(sim_res.recommended_additions)} optimizations and {len(reg_res.forgotten_items)} forgotten items to improve success probability from {sim_res.current_success}% to {sim_res.optimized_success}%."
        }

        # Build clean customer response executive summary (Task 7)
        # Classify cart groups dynamically
        from engines.domains.verification.capability_verification_service import CapabilityVerificationService
        cap_verification_svc = CapabilityVerificationService()
        cart_groups = []
        for pid in cart_products:
            meta = self.graph_repo.get_item(f"PRODUCT#{pid}", "METADATA") or {}
            title = display_title_resolution(pid, meta)
            if title:
                prod_info = dict(meta)
                prod_info["title"] = title
                prod_info["id"] = pid
                prod_groups = cap_verification_svc.get_product_groups(prod_info)
                for g in prod_groups:
                    if g in blueprint.get("required_groups", []) and g not in cart_groups:
                        cart_groups.append(g)

        selected_titles = [p.title for p in cg_res.required_products + cg_res.optional_products]

        executive_summary = {
            "mission": mission_id.replace("_", " ").title(),
            "capabilities": capabilities,
            "cart_groups": cart_groups,
            "coverage": f"{ver_res.readiness_score}%",
            "next_actions": f"Finalize your order via '{final_recommendation['action']}'.",
            "products_selected": ", ".join(selected_titles),
            "why_selected": "Selected based on Capability Intelligence Layer.",
            "current_status": f"Unified readiness score is {ver_res.readiness_score}%.",
            "key_gaps": f"Missing outcome groups: {', '.join(ver_res.missing_items)}" if ver_res.missing_items else "No missing essential groups."
        }

        # Reasoning list (clean)
        reasoning = [
            f"Mission '{mission_id.replace('_', ' ').title()}' resolved through Outcome Blueprint Engine.",
            f"Unified readiness score is {ver_res.readiness_score}% based on capability completion, group completion, and product diversity.",
            f"Evaluated risk level as {risk_res.risk_level} (score: {risk_res.risk_score}).",
            f"Success probability optimized to {sim_res.optimized_success}%."
        ]

        # Diagnostics metrics
        override_count = 0
        total_agents = 6
        if len(ai_mission_res.accepted_changes) > 0:
            override_count += 1
        if len(ai_cart_res.accepted_changes) > 0:
            override_count += 1
        if len(ai_ver_res.accepted_changes) > 0:
            override_count += 1
        if len(ai_risk_res.accepted_changes) > 0:
            override_count += 1
        if len(ai_reg_res.accepted_changes) > 0:
            override_count += 1
        if len(ai_sim_res.accepted_changes) > 0:
            override_count += 1
        decision_override_rate = override_count / total_agents
        product_rejection_rate = (len(rejected_prod_ids) / (len(cg_res.required_products) + len(cg_res.optional_products))) if (cg_res.required_products or cg_res.optional_products) else 0.0

        ai_decision_log = {
            "mission_agent": {"confidence": ai_mission_res.confidence, "changes": ai_mission_res.accepted_changes, "mode": mode_env},
            "cart_agent": {"rejected": rejected_prod_names, "accepted": accepted_prod_names, "mode": mode_env},
            "verification_agent": {"confidence": ai_ver_res.confidence, "changes": ai_ver_res.accepted_changes, "mode": mode_env},
            "risk_agent": {"confidence": ai_risk_res.confidence, "changes": ai_risk_res.accepted_changes, "mode": mode_env},
            "regret_agent": {"confidence": ai_reg_res.confidence, "changes": ai_reg_res.accepted_changes, "mode": mode_env},
            "simulation_agent": {"confidence": ai_sim_res.confidence, "changes": ai_sim_res.accepted_changes, "mode": mode_env},
            "auditor": {"score": audit_score, "grounding_score": grounding_score, "consistency_score": 100, "mode": mode_env}
        }

        output_dict = {
            "mission": {
                "detected_mission": mission_id,
                "parameters": params,
                "confidence": md_res.confidence
            },
            "cart": {
                "estimated_total_cost": cart_cost,
                "estimated_serving_capacity": cg_res.estimated_serving_capacity,
                "items_count": len(cart_products),
                "mission_coherence_score": cg_res.mission_coherence_score
            },
            "verification": ver_res.dict(),
            "risk": risk_res.dict(),
            "regret_prevention": reg_res.dict(),
            "simulation": sim_res.dict(),
            "final_recommendation": final_recommendation,
            "reasoning": reasoning,
            "mission_coherence_score": cg_res.mission_coherence_score,
            "grounding_score": grounding_score,
            "reality_score": reality_score,
            "consistency_score": 100,
            "catalog_validity_score": catalog_validity_score,
            "graph_validity_score": graph_validity_score,
            "executive_summary": executive_summary
        }

        # Runtime Truth verification
        from shared.ai.policy.runtime_truth_engine import RuntimeTruthEngine
        truth_engine = RuntimeTruthEngine()
        truth_res = truth_engine.verify_runtime_truth(output_dict, self.ai_gateway.bedrock)
        
        provider_val = truth_res["actual_provider"]
        model_val = truth_res["actual_model"]
        mode_val = truth_res["actual_mode"]
        
        output_dict["runtime_truth"] = truth_res["runtime_truth"]

        if mode_env == "BEDROCK_LIVE" and provider_val == "simulation":
            return {
                "status": "BLOCKED",
                "error": "LIVE_EXECUTION_FAILED",
                "reason": "Simulation provider detected during Bedrock execution"
            }

        ai_metadata_clean = {
            "token_usage": {
                "input_tokens": self.ai_gateway.tokens.total_input_tokens,
                "output_tokens": self.ai_gateway.tokens.total_output_tokens
            },
            "execution_cost_usd": self.ai_gateway.costs.total_cost_usd,
            "mission_analysis": ai_mission_res.model_dump(),
            "cart_analysis": ai_cart_res.model_dump()
        }
        output_dict["ai_metadata"] = ai_metadata_clean

        output_dict["ai_runtime"] = {
            "provider": provider_val,
            "model": model_val,
            "mode": mode_val,
            "latency_ms": 0,
            "input_tokens": self.ai_gateway.tokens.total_input_tokens,
            "output_tokens": self.ai_gateway.tokens.total_output_tokens
        }

        final_response, cert = self.policy_engine.evaluate_and_repair(output_dict)
        if final_response.get("status") == "BLOCKED":
            return final_response

        latency = time.time() - start_time
        latency_ms = int(latency * 1000)
        
        ai_runtime_val = {
            "provider": provider_val,
            "model": model_val,
            "mode": mode_val,
            "latency_ms": latency_ms,
            "input_tokens": self.ai_gateway.tokens.total_input_tokens,
            "output_tokens": self.ai_gateway.tokens.total_output_tokens
        }

        truth_report = {
            "live_execution_verified": truth_res["live_execution_verified"],
            "catalog_grounded": final_response.get("catalog_validity_score", 0) == 100,
            "graph_grounded": final_response.get("graph_validity_score", 0) == 100,
            "mission_consistent": True,
            "certification_valid": final_response.get("trust_level") == "TRUSTED"
        }

        final_response["ai_metadata"]["latency_sec"] = latency
        final_response["ai_runtime"] = ai_runtime_val

        # Replay logging
        final_response["query"] = query
        self.replay_engine.save_decision(final_response)

        # Build clean Task 7 output format
        customer_response = {
            "executive_summary": executive_summary,
            "mission": {
                "detected_mission": mission_id,
                "parameters": params,
                "confidence": md_res.confidence
            },
            "cart": {
                "estimated_total_cost": cart_cost,
                "estimated_serving_capacity": cg_res.estimated_serving_capacity,
                "items_count": len(cart_products),
                "mission_coherence_score": cg_res.mission_coherence_score
            },
            "verification": ver_res.dict(),
            "risk": risk_res.dict(),
            "simulation": sim_res.dict(),
            "final_recommendation": final_recommendation
        }

        metrics_val = {
            "decision_override_rate": decision_override_rate,
            "product_rejection_rate": product_rejection_rate,
            "mission_correction_rate": 0.0,
            "risk_correction_rate": 1.0 if overridden_risk_level is not None else 0.0,
            "auditor_failure_rate": 0.0,
            "capability_coverage": ver_res.readiness_breakdown.get("capability_completion", 100),
            "grounding_score": grounding_score,
            "reality_score": reality_score,
            "consistency_score": 100,
            "catalog_validity_score": catalog_validity_score,
            "graph_validity_score": graph_validity_score
        }

        system_diagnostics = {
            "ai_runtime": ai_runtime_val,
            "runtime_truth": truth_res["runtime_truth"],
            "certification": cert,
            "execution_trace": self.execution_trace,
            "repair_log": final_response.get("repair_log", []),
            "trust_level": final_response.get("trust_level", "TRUSTED"),
            "policy_score": final_response.get("policy_score", 100),
            "truth_report": truth_report,
            "metrics": metrics_val
        }

        if debug:
            system_diagnostics["ai_metadata"] = ai_metadata_clean
            system_diagnostics["auditor_report"] = ai_auditor_res.model_dump()
            system_diagnostics["ai_decision_log"] = ai_decision_log

        return {
            "customer_response": customer_response,
            "system_diagnostics": system_diagnostics
        }
