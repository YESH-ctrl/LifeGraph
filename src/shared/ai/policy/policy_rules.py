import re
from typing import Dict, Any, List, Tuple

class PolicyRule:
    def __init__(
        self,
        rule_id: str,
        description: str,
        severity: str,  # "CRITICAL" or "WARNING"
        validation_func,
        repair_func
    ):
        self.id = rule_id
        self.description = description
        self.severity = severity
        self.validate = validation_func
        self.repair = repair_func

# Helper to check UUID pattern
def is_uuid_like(s: str) -> bool:
    if not s:
        return False
    s = str(s).strip()
    uuid_pattern = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
    return bool(re.search(uuid_pattern, s))

# --- 1. RULE_EMPTY_CART ---
def val_empty_cart(state: Dict[str, Any]) -> bool:
    items_count = state.get("cart", {}).get("items_count", 0)
    if items_count == 0:
        # Check if score variables are inconsistent
        has_inconsistency = (
            state.get("verification", {}).get("readiness_score", 0) != 0 or
            state.get("risk", {}).get("risk_level") != "HIGH" or
            state.get("simulation", {}).get("optimized_success", 0) != 0 or
            state.get("final_recommendation", {}).get("action") != "Review Cart"
        )
        return has_inconsistency
    return False

def rep_empty_cart(state: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    logs = []
    
    # Repair Verification
    old_readiness = state.get("verification", {}).get("readiness_score", 0)
    if old_readiness != 0:
        state["verification"]["readiness_score"] = 0
        logs.append({"rule": "RULE_EMPTY_CART", "field": "verification.readiness_score", "old_value": old_readiness, "new_value": 0})
        
    # Repair Risk
    old_risk_level = state.get("risk", {}).get("risk_level", "LOW")
    if old_risk_level != "HIGH":
        state["risk"]["risk_level"] = "HIGH"
        state["risk"]["risk_score"] = 100
        logs.append({"rule": "RULE_EMPTY_CART", "field": "risk.risk_level", "old_value": old_risk_level, "new_value": "HIGH"})
        
    # Repair Simulation
    old_success = state.get("simulation", {}).get("optimized_success", 0)
    if old_success != 0:
        state["simulation"]["optimized_success"] = 0
        state["simulation"]["current_success"] = 0
        state["simulation"]["improvement"] = 0
        logs.append({"rule": "RULE_EMPTY_CART", "field": "simulation.optimized_success", "old_value": old_success, "new_value": 0})
        
    # Repair Action
    old_action = state.get("final_recommendation", {}).get("action", "Proceed to Checkout")
    if old_action != "Review Cart":
        state["final_recommendation"]["action"] = "Review Cart"
        state["final_recommendation"]["message"] = "Cart is empty. Please select required products."
        logs.append({"rule": "RULE_EMPTY_CART", "field": "final_recommendation.action", "old_value": old_action, "new_value": "Review Cart"})
        
    return state, logs

# --- Configurable Risk Thresholds (Phase 7.1 Task 5) ---
RISK_THRESHOLDS = {
    "critical_missing_for_high": 5,    # critical_missing >= 5 → risk must be HIGH minimum
    "critical_missing_for_critical": 10  # critical_missing >= 10 → risk must be CRITICAL
}

# --- 2. RULE_INVALID_RISK ---
def val_invalid_risk(state: Dict[str, Any]) -> bool:
    crit_missing = len(state.get("verification", {}).get("critical_missing", []))
    risk_level = state.get("risk", {}).get("risk_level", "LOW")
    # If critical_missing >= 10, risk must be CRITICAL
    if crit_missing >= RISK_THRESHOLDS["critical_missing_for_critical"] and risk_level in ["LOW", "MEDIUM", "HIGH"]:
        return True
    # If critical_missing >= 5, risk must be at least HIGH
    if crit_missing >= RISK_THRESHOLDS["critical_missing_for_high"] and risk_level in ["LOW", "MEDIUM"]:
        return True
    return False

def rep_invalid_risk(state: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    logs = []
    crit_missing = len(state.get("verification", {}).get("critical_missing", []))
    old_level = state["risk"]["risk_level"]
    if crit_missing >= RISK_THRESHOLDS["critical_missing_for_critical"]:
        state["risk"]["risk_level"] = "CRITICAL"
        state["risk"]["risk_score"] = 90
        logs.append({"rule": "RULE_INVALID_RISK", "field": "risk.risk_level", "old_value": old_level, "new_value": "CRITICAL"})
    else:
        state["risk"]["risk_level"] = "HIGH"
        state["risk"]["risk_score"] = 75
        logs.append({"rule": "RULE_INVALID_RISK", "field": "risk.risk_level", "old_value": old_level, "new_value": "HIGH"})
    return state, logs

# --- 3. RULE_INVALID_SUCCESS ---
def val_invalid_success(state: Dict[str, Any]) -> bool:
    readiness = state.get("verification", {}).get("readiness_score", 0)
    success = state.get("simulation", {}).get("optimized_success", 0)
    if readiness <= 10 and success >= 80:
        return True
    return False

def rep_invalid_success(state: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    logs = []
    old_success = state["simulation"]["optimized_success"]
    state["simulation"]["optimized_success"] = 25
    state["simulation"]["improvement"] = 15
    logs.append({"rule": "RULE_INVALID_SUCCESS", "field": "simulation.optimized_success", "old_value": old_success, "new_value": 25})
    return state, logs

# --- 4. RULE_INVALID_READINESS ---
def val_invalid_readiness(state: Dict[str, Any]) -> bool:
    readiness = state.get("verification", {}).get("readiness_score", 0)
    crit_missing = len(state.get("verification", {}).get("critical_missing", []))
    if readiness == 100 and crit_missing > 0:
        return True
    return False

def rep_invalid_readiness(state: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    logs = []
    old_readiness = state["verification"]["readiness_score"]
    crit_missing = len(state["verification"]["critical_missing"])
    new_readiness = max(0, 100 - (crit_missing * 10))
    state["verification"]["readiness_score"] = new_readiness
    logs.append({"rule": "RULE_INVALID_READINESS", "field": "verification.readiness_score", "old_value": old_readiness, "new_value": new_readiness})
    return state, logs

# --- 5. RULE_UUID_LEAK ---
def val_uuid_leak(state: Dict[str, Any]) -> bool:
    # Scan reasoning lists or titles
    for reason in state.get("reasoning", []):
        if is_uuid_like(reason):
            return True
    return False

def rep_uuid_leak(state: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    logs = []
    cleaned_reasoning = []
    for idx, r in enumerate(state.get("reasoning", [])):
        if is_uuid_like(r):
            # Strip out UUID pattern
            cleaned = re.sub(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', '[CLEANED]', r)
            cleaned_reasoning.append(cleaned)
            logs.append({"rule": "RULE_UUID_LEAK", "field": f"reasoning[{idx}]", "old_value": r, "new_value": cleaned})
        else:
            cleaned_reasoning.append(r)
    state["reasoning"] = cleaned_reasoning
    return state, logs

# --- 6. RULE_CATALOG_VIOLATION ---
def val_catalog_violation(state: Dict[str, Any]) -> bool:
    # Handled inside policy engine using catalog lookup directly
    return False

def rep_catalog_violation(state: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    return state, []

# --- 7. RULE_GROUNDING_FAILURE ---
def val_grounding_failure(state: Dict[str, Any]) -> bool:
    # Handled inside policy engine by scanning changes evidence
    return False

def rep_grounding_failure(state: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    return state, []


# --- REGISTER ALL RULES ---
RULES = [
    PolicyRule("RULE_EMPTY_CART", "Empty cart must force scores and success probability to zero and trigger Review Cart", "CRITICAL", val_empty_cart, rep_empty_cart),
    PolicyRule("RULE_INVALID_RISK", "High critical missing items cannot coexist with LOW or MEDIUM risk scores", "CRITICAL", val_invalid_risk, rep_invalid_risk),
    PolicyRule("RULE_INVALID_SUCCESS", "High simulation success probability cannot coexist with extremely low readiness", "CRITICAL", val_invalid_success, rep_invalid_success),
    PolicyRule("RULE_INVALID_READINESS", "Readiness score cannot be 100% if critical missing items are present", "CRITICAL", val_invalid_readiness, rep_invalid_readiness),
    PolicyRule("RULE_UUID_LEAK", "Raw UUID patterns must not leak in reasoning fields", "CRITICAL", val_uuid_leak, rep_uuid_leak)
]
