import json
import logging
from typing import List, Dict, Any

from .ai_gateway import AIGateway
from .schemas import (
    DecisionDelta,
    MissionAnalysisOutput,
    CartAnalysisOutput,
    VerificationAnalysisOutput,
    RiskAnalysisOutput,
    RegretAnalysisOutput,
    SimulationAnalysisOutput,
    AuditorAnalysisOutput
)

logger = logging.getLogger(__name__)

class MissionIntelligenceAgent:
    def __init__(self, gateway: AIGateway):
        self.gateway = gateway

    def analyze(self, query: str, original_mission: str) -> DecisionDelta[MissionAnalysisOutput]:
        logger.info("Executing MissionIntelligenceAgent...")
        original_json = json.dumps({"detected_mission": original_mission})
        return self.gateway.execute_agent(
            agent_name="mission",
            schema_class=DecisionDelta[MissionAnalysisOutput],
            query=query,
            original_json=original_json
        )

class CartIntelligenceAgent:
    def __init__(self, gateway: AIGateway):
        self.gateway = gateway

    def analyze(self, mission_id: str, products: List[Dict[str, Any]]) -> DecisionDelta[CartAnalysisOutput]:
        logger.info("Executing CartIntelligenceAgent...")
        products_json = json.dumps(products, default=str)
        return self.gateway.execute_agent(
            agent_name="cart",
            schema_class=DecisionDelta[CartAnalysisOutput],
            mission_id=mission_id,
            products_json=products_json
        )

class VerificationIntelligenceAgent:
    def __init__(self, gateway: AIGateway):
        self.gateway = gateway

    def analyze(self, mission_id: str, cart_items: List[str], original_verification: Dict[str, Any]) -> DecisionDelta[VerificationAnalysisOutput]:
        logger.info("Executing VerificationIntelligenceAgent...")
        original_json = json.dumps(original_verification, default=str)
        return self.gateway.execute_agent(
            agent_name="verification",
            schema_class=DecisionDelta[VerificationAnalysisOutput],
            mission_id=mission_id,
            cart_items=json.dumps(cart_items),
            original_json=original_json
        )

class RiskIntelligenceAgent:
    def __init__(self, gateway: AIGateway):
        self.gateway = gateway

    def analyze(self, mission_id: str, cart_items: List[str], original_risk: Dict[str, Any]) -> DecisionDelta[RiskAnalysisOutput]:
        logger.info("Executing RiskIntelligenceAgent...")
        original_json = json.dumps(original_risk, default=str)
        return self.gateway.execute_agent(
            agent_name="risk",
            schema_class=DecisionDelta[RiskAnalysisOutput],
            mission_id=mission_id,
            cart_items=json.dumps(cart_items),
            original_json=original_json
        )

class RegretPreventionIntelligenceAgent:
    def __init__(self, gateway: AIGateway):
        self.gateway = gateway

    def analyze(self, mission_id: str, cart_items: List[str], original_regret: Dict[str, Any]) -> DecisionDelta[RegretAnalysisOutput]:
        logger.info("Executing RegretPreventionIntelligenceAgent...")
        original_json = json.dumps(original_regret, default=str)
        return self.gateway.execute_agent(
            agent_name="regret",
            schema_class=DecisionDelta[RegretAnalysisOutput],
            mission_id=mission_id,
            cart_items=json.dumps(cart_items),
            original_json=original_json
        )

class SimulationIntelligenceAgent:
    def __init__(self, gateway: AIGateway):
        self.gateway = gateway

    def analyze(self, original_simulation: Dict[str, Any], additions: List[str]) -> DecisionDelta[SimulationAnalysisOutput]:
        logger.info("Executing SimulationIntelligenceAgent...")
        original_json = json.dumps(original_simulation, default=str)
        return self.gateway.execute_agent(
            agent_name="simulation",
            schema_class=DecisionDelta[SimulationAnalysisOutput],
            original_json=original_json,
            additions=json.dumps(additions)
        )

class OutcomeAuditorAgent:
    def __init__(self, gateway: AIGateway):
        self.gateway = gateway

    def audit(self, agent_logs: List[Dict[str, Any]]) -> DecisionDelta[AuditorAnalysisOutput]:
        logger.info("Executing OutcomeAuditorAgent...")
        agent_logs_json = json.dumps(agent_logs, default=str)
        return self.gateway.execute_agent(
            agent_name="auditor",
            schema_class=DecisionDelta[AuditorAnalysisOutput],
            agent_logs_json=agent_logs_json
        )

