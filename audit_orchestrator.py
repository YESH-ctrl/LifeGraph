import sys, os, json
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

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
from foundation.graph.repository import GraphRepository

query = "I am planning biryani for 20 guests"
audit = {}

# --- STAGE 1: Mission Detection ---
md_svc = MissionDetectionService()
md_req = MissionDetectionRequest(text=query, user_id="system", session_id="audit")
md_res = md_svc.detect(md_req)
mission_id = md_res.detected_mission
params = md_res.parameters

audit["1_mission_detection"] = {
    "input": {"query": query},
    "output": {
        "detected_mission": mission_id,
        "confidence": md_res.confidence,
        "parameters": params
    }
}

# --- STAGE 2: Cart Generation ---
cg_svc = CartGenerationService()
cg_req = CartGenerationRequest(mission_id=mission_id, parameters=params)

# Check what graph returns for REQUIRES
repo = GraphRepository()
requires_edges_raw = repo.query_by_pk(f"MISSION#{mission_id}", "REQUIRES#")
optional_edges_raw = repo.query_by_pk(f"MISSION#{mission_id}", "OPTIONAL#")

cg_res = cg_svc.generate_cart(cg_req)

# Filter CRITICAL like master_orchestrator does
cart_products = [p.product_id for p in cg_res.required_products if p.priority == "CRITICAL"]
cart_cost = sum(p.estimated_cost for p in cg_res.required_products if p.priority == "CRITICAL")

audit["2_cart_generation"] = {
    "input": {"mission_id": mission_id, "parameters": params},
    "graph_REQUIRES_edges_count": len(requires_edges_raw),
    "graph_REQUIRES_edges": [e.get("SK") for e in requires_edges_raw],
    "graph_OPTIONAL_edges_count": len(optional_edges_raw),
    "all_required_products": [{"id": p.product_id, "priority": p.priority, "cost": p.estimated_cost} for p in cg_res.required_products],
    "all_optional_products": [{"id": p.product_id, "priority": p.priority} for p in cg_res.optional_products],
    "CRITICAL_only_filter": cart_products,
    "CRITICAL_only_count": len(cart_products),
    "total_required_before_filter": len(cg_res.required_products),
    "cart_cost": cart_cost
}

# --- STAGE 3: Verification ---
ver_svc = VerificationService()
ver_req = VerificationRequest(mission_id=mission_id, cart_products=cart_products)
ver_res = ver_svc.verify(ver_req)

audit["3_verification"] = {
    "input": {"mission_id": mission_id, "cart_products": cart_products, "cart_count": len(cart_products)},
    "output": {
        "readiness_score": ver_res.readiness_score,
        "required_items": ver_res.required_items,
        "missing_items": ver_res.missing_items,
        "critical_missing": ver_res.critical_missing,
        "important_missing": ver_res.important_missing,
        "optional_missing": ver_res.optional_missing,
        "recommended_products": ver_res.recommended_products
    }
}

# --- STAGE 4: Risk ---
risk_svc = RiskService()
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
risk_res = risk_svc.analyze(risk_req)

audit["4_risk"] = {
    "input": {
        "cart_products": cart_products,
        "readiness_score": ver_res.readiness_score,
        "critical_missing": ver_res.critical_missing,
        "budget": params.get("budget"),
        "total_cost": cart_cost
    },
    "output": {
        "risk_score": risk_res.risk_score,
        "risk_level": risk_res.risk_level,
        "risks": [{"type": r.type, "severity": r.severity, "reason": r.reason} for r in risk_res.risks]
    }
}

# --- STAGE 5: Regret Prevention ---
reg_svc = RegretPreventionService()
reg_req = RegretPreventionRequest(mission_id=mission_id, cart_products=cart_products)
reg_res = reg_svc.evaluate(reg_req)

audit["5_regret_prevention"] = {
    "input": {"mission_id": mission_id, "cart_products": cart_products},
    "output": {
        "forgotten_items": reg_res.forgotten_items,
        "impact_score": reg_res.impact_score
    }
}

# --- STAGE 6: Simulation ---
sim_svc = SimulatorService()
sim_req = SimulatorRequest(
    readiness_score=ver_res.readiness_score,
    risk_score=risk_res.risk_score,
    recommended_additions=ver_res.recommended_products,
    forgotten_items=reg_res.forgotten_items
)
sim_res = sim_svc.run_mission_simulation(sim_req)

audit["6_simulation"] = {
    "input": {
        "readiness_score": ver_res.readiness_score,
        "risk_score": risk_res.risk_score,
        "recommended_additions": ver_res.recommended_products,
        "forgotten_items": reg_res.forgotten_items
    },
    "output": {
        "current_success": sim_res.current_success,
        "optimized_success": sim_res.optimized_success,
        "improvement": sim_res.improvement
    }
}

# Write output
with open("orchestrator_execution_audit.json", "w") as f:
    json.dump(audit, f, indent=2, default=str)

print(json.dumps(audit, indent=2, default=str))
