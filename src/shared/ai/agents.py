import json
import logging
from typing import List, Dict, Any, TypeVar, Type
from pydantic import BaseModel

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
T = TypeVar("T", bound=BaseModel)

class MissionIntelligenceAgent:
    def __init__(self, gateway: AIGateway):
        self.gateway = gateway

    def analyze(self, query: str) -> DecisionDelta[MissionAnalysisOutput]:
        logger.info("Executing MissionIntelligenceAgent...")
        return self.gateway.execute_agent(
            agent_name="mission",
            schema_class=DecisionDelta[MissionAnalysisOutput],
            query=query
        )

class CartIntelligenceAgent:
    def __init__(self, gateway: AIGateway):
        self.gateway = gateway

    def analyze(self, mission: str, capabilities: List[str], blueprint: Dict[str, Any]) -> DecisionDelta[CartAnalysisOutput]:
        logger.info("Executing CartIntelligenceAgent...")
        return self.gateway.execute_agent(
            agent_name="cart",
            schema_class=DecisionDelta[CartAnalysisOutput],
            mission=mission,
            capabilities=json.dumps(capabilities),
            blueprint=json.dumps(blueprint)
        )

class VerificationIntelligenceAgent:
    def __init__(self, gateway: AIGateway):
        self.gateway = gateway

    def analyze(self, cart: List[str], blueprint: Dict[str, Any]) -> DecisionDelta[VerificationAnalysisOutput]:
        logger.info("Executing VerificationIntelligenceAgent...")
        return self.gateway.execute_agent(
            agent_name="verification",
            schema_class=DecisionDelta[VerificationAnalysisOutput],
            cart=json.dumps(cart),
            blueprint=json.dumps(blueprint)
        )

class RiskIntelligenceAgent:
    def __init__(self, gateway: AIGateway):
        self.gateway = gateway

    def analyze(self, verification: Dict[str, Any]) -> DecisionDelta[RiskAnalysisOutput]:
        logger.info("Executing RiskIntelligenceAgent...")
        return self.gateway.execute_agent(
            agent_name="risk",
            schema_class=DecisionDelta[RiskAnalysisOutput],
            verification=json.dumps(verification)
        )

class RegretPreventionIntelligenceAgent:
    def __init__(self, gateway: AIGateway):
        self.gateway = gateway

    def analyze(self, cart: List[str], blueprint: Dict[str, Any]) -> DecisionDelta[RegretAnalysisOutput]:
        logger.info("Executing RegretPreventionIntelligenceAgent...")
        return self.gateway.execute_agent(
            agent_name="regret",
            schema_class=DecisionDelta[RegretAnalysisOutput],
            cart=json.dumps(cart),
            blueprint=json.dumps(blueprint)
        )

class SimulationIntelligenceAgent:
    def __init__(self, gateway: AIGateway):
        self.gateway = gateway

    def analyze(self, verification: Dict[str, Any], risk: Dict[str, Any]) -> DecisionDelta[SimulationAnalysisOutput]:
        logger.info("Executing SimulationIntelligenceAgent...")
        return self.gateway.execute_agent(
            agent_name="simulation",
            schema_class=DecisionDelta[SimulationAnalysisOutput],
            verification=json.dumps(verification),
            risk=json.dumps(risk)
        )

class OutcomeAuditorAgent:
    def __init__(self, gateway: AIGateway):
        self.gateway = gateway

    def audit(self, metrics: Dict[str, Any]) -> DecisionDelta[AuditorAnalysisOutput]:
        logger.info("Executing OutcomeAuditorAgent...")
        return self.gateway.execute_agent(
            agent_name="auditor",
            schema_class=DecisionDelta[AuditorAnalysisOutput],
            metrics=json.dumps(metrics)
        )
