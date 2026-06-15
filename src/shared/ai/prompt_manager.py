import os
import string
from typing import Dict, Any, Optional

class SafeFormatter(string.Formatter):
    def get_value(self, key, args, kwargs):
        if isinstance(key, str):
            # If key is missing from kwargs, return the key as placeholder to prevent KeyError
            return kwargs.get(key, f"{{{key}}}")
        return string.Formatter.get_value(self, key, args, kwargs)

class PromptManager:
    def __init__(self):
        self._registry: Dict[str, Dict[str, Any]] = {}
        self._register_defaults()

    def register_template(self, name: str, version: str, template: str, metadata: Optional[Dict[str, Any]] = None):
        if name not in self._registry:
            self._registry[name] = {}
        self._registry[name][version] = {
            "template": template,
            "metadata": metadata or {}
        }

    def render(self, name: str, version: str, **kwargs) -> str:
        if name not in self._registry or version not in self._registry[name]:
            raise ValueError(f"Template {name} with version {version} is not registered.")
        
        template_str = self._registry[name][version]["template"]
        return SafeFormatter().format(template_str, **kwargs)

    def get_metadata(self, name: str, version: str) -> Dict[str, Any]:
        if name not in self._registry or version not in self._registry[name]:
            return {}
        return self._registry[name][version]["metadata"]

    def _register_defaults(self):
        # 1. Mission Prompt (Task 6: {"query": query})
        self.register_template(
            name="mission",
            version="1.0.0",
            template="""You are the Mission Intelligence Agent.
Evaluate the user query: "{query}"

Identify:
- Hidden goals (e.g. fat_loss, reduce_sugar, healthy_eating)
- User constraints (e.g. diabetic, vegan, allergy triggers)
- Lifestyle indicators (e.g. bulk_shopper, clean_eating)

CRITICAL: Never infer or add any user constraints, health conditions, or lifestyle indicators unless they are explicitly present in the query or user profile context. Never assume unsupported constraints.

Output a JSON object matching this DecisionDelta schema:
{{
  "original_output": {{}},
  "ai_analysis": {{
    "detected_mission": "monthly_grocery_refill",
    "sub_goals": ["reduce_sugar", "fat_loss"],
    "user_constraints": [],
    "lifestyle_indicators": ["healthy_eating"]
  }},
  "recommended_changes": [],
  "accepted_changes": [],
  "rejected_changes": [],
  "confidence": 0.95,
  "reasoning": ["Found low calorie / lose weight keywords", "Identified relevant user constraints from query"]
}}""",
            metadata={"description": "Baseline mission classification"}
        )

        # 2. Cart Prompt (Task 6: {"mission": mission, "capabilities": capabilities, "blueprint": blueprint})
        self.register_template(
            name="cart",
            version="1.0.0",
            template="""You are the Cart Intelligence Agent.
Review the candidate products for the mission "{mission}".
Required Capabilities: {capabilities}
Blueprint Outcome Targets: {blueprint}

Detect contradictions based on user constraints (e.g., Reject chocolate/sugar/high-carb snacks in weight_loss_journey or diabetic, reject dairy/eggs in vegan).
Classify each item status as APPROVED, QUESTIONABLE, or REJECTED.

Output a JSON object matching this DecisionDelta schema:
{{
  "original_output": {{}},
  "ai_analysis": {{
    "items": [
      {{
        "product_id": "product_123",
        "title": "Example Product",
        "priority": "CRITICAL",
        "reason": "Correct alignment",
        "status": "APPROVED",
        "feedback": null
      }}
    ],
    "mission_coherence_score": 90
  }},
  "recommended_changes": [],
  "accepted_changes": [],
  "rejected_changes": [],
  "confidence": 0.95,
  "reasoning": ["Detected alignment with required capabilities"]
}}""",
            metadata={"description": "Baseline cart alignment and safety filter validation"}
        )

        # 3. Verification Prompt (Task 6: {"cart": cart, "blueprint": blueprint})
        self.register_template(
            name="verification",
            version="1.0.0",
            template="""You are the Verification Intelligence Agent.
Verify cart items: {cart}
Outcome Blueprint: {blueprint}

Evaluate whether missing groups or capabilities truly matter. Adjust readiness accordingly.

CRITICAL: Predict readiness score conservatively. Do not raise the readiness score dramatically. Ensure it reflects the actual percentage of critical/important items present. Optional missing items may slightly improve readiness, but do not exceed the reality threshold boundaries.

Output a JSON object matching this DecisionDelta schema:
{{
  "original_output": {{}},
  "ai_analysis": {{
    "readiness_score": 85,
    "critical_missing": [],
    "important_missing": [],
    "recommended_products": []
  }},
  "recommended_changes": [
    {{"type": "override_readiness", "score": 85, "reason": "Missing non-essential groups, restoring readiness"}}
  ],
  "accepted_changes": [
    {{"type": "override_readiness", "score": 85}}
  ],
  "rejected_changes": [],
  "confidence": 0.95,
  "reasoning": ["Readiness score corrected because missing items belong to non-essential outcome groups"]
}}""",
            metadata={"description": "Baseline readiness evaluation"}
        )

        # 4. Risk Prompt (Task 6: {"verification": verification})
        self.register_template(
            name="risk",
            version="1.0.0",
            template="""You are the Risk Intelligence Agent.
Evaluate the failure probability based on verification: {verification}

Determine actual mission risk (e.g., if missing items are non-essential outcome groups, risk is LOW, not CRITICAL). Overwrite risk values.

CRITICAL: Adhere to strict risk thresholds: if there are 5 or more critical missing items, the risk score MUST be at least 65 and risk level at least HIGH. If there are 10 or more critical missing items, risk score must be at least 80 and level CRITICAL. Learn these thresholds and predict risk score/level accordingly.

Output a JSON object matching this DecisionDelta schema:
{{
  "original_output": {{}},
  "ai_analysis": {{
    "risk_score": 15,
    "risk_level": "LOW",
    "risks": []
  }},
  "recommended_changes": [
    {{"type": "override_risk", "level": "LOW", "score": 15}}
  ],
  "accepted_changes": [
    {{"type": "override_risk", "level": "LOW", "score": 15}}
  ],
  "rejected_changes": [],
  "confidence": 0.95,
  "reasoning": ["Lowered risk level from HIGH to LOW since missing items are not critical blockers"]
}}""",
            metadata={"description": "Baseline risk calculation"}
        )

        # 5. Regret Prompt (Task 6: {"cart": cart, "blueprint": blueprint})
        self.register_template(
            name="regret",
            version="1.0.0",
            template="""You are the Regret Prevention Agent.
Check vital components based on cart items: {cart}
Outcome Blueprint: {blueprint}

Predict genuine user regret. For weight loss, recommend Meal Prep Containers, Kitchen Scale, or Protein Snacks.

Output a JSON object matching this DecisionDelta schema:
{{
  "original_output": {{}},
  "ai_analysis": {{
    "forgotten_items": ["meal_prep_containers", "kitchen_scale"],
    "impact_score": 40
  }},
  "recommended_changes": [
    {{"type": "add_accessory", "name": "meal_prep_containers"}}
  ],
  "accepted_changes": [
    {{"type": "add_accessory", "name": "meal_prep_containers"}}
  ],
  "rejected_changes": [],
  "confidence": 0.95,
  "reasoning": ["Recommended meal prep accessories to ensure healthy lifestyle consistency"]
}}""",
            metadata={"description": "Baseline forgotten items estimation"}
        )

        # 6. Simulation Prompt (Task 6: {"verification": verification, "risk": risk})
        self.register_template(
            name="simulation",
            version="1.0.0",
            template="""You are the Simulation Agent.
Analyze simulation metrics based on verification: {verification} and risk: {risk}

Explain outcome success probability factors (fiber/protein coverage, calorie reduction, risks).

CRITICAL: Adhere to strict success score boundaries. Success probability cannot be high if readiness is low or risk is high. Current success should align with readiness. Optimized success must be bounded by the formula: optimized_success <= readiness_score + 30. Learn these boundaries and predict success scores accordingly.

Output a JSON object matching this DecisionDelta schema:
{{
  "original_output": {{}},
  "ai_analysis": {{
    "current_success": 45,
    "optimized_success": 85,
    "improvement": 40,
    "recommended_additions": []
  }},
  "recommended_changes": [],
  "accepted_changes": [],
  "rejected_changes": [],
  "confidence": 0.95,
  "reasoning": ["Diet success increases due to protein coverage and calorie reduction"]
}}""",
            metadata={"description": "Baseline simulation explainability"}
        )

        # 7. Auditor Prompt (Task 6: {"metrics": metrics})
        self.register_template(
            name="auditor",
            version="1.0.0",
            template="""You are the Outcome Auditor Agent.
Validate all agent outputs and check compliance using metrics: {metrics}

Output a JSON object matching this DecisionDelta schema:
{{
  "original_output": {{}},
  "ai_analysis": {{
    "overall_confidence_score": 0.98,
    "audit_score": 95,
    "grounding_score": 95,
    "consistency_score": 98,
    "failures": [],
    "warnings": [],
    "improvement_suggestions": []
  }},
  "recommended_changes": [],
  "accepted_changes": [],
  "rejected_changes": [],
  "confidence": 0.95,
  "reasoning": ["Compliance check passed based on outcomes"]
}}""",
            metadata={"description": "Baseline audit compliance evaluation"}
        )
