import json
import logging
import math
import re
from typing import Any, Dict, List, Tuple

from engines.agents.base_agent import BaseAgent
from ingestion.product_intelligence import APPROVED_MISSIONS
from foundation.domains.missions.detection_service import DetectionService
from foundation.graph.service import GraphService
from foundation.shared.repositories.mission_repository import MissionRepository

logger = logging.getLogger(__name__)

FROZEN_MISSION_CATALOG = frozenset(APPROVED_MISSIONS.keys())

# Catalog IDs that differ from DynamoDB mission_id values
MISSION_DB_ALIASES: Dict[str, str] = {
    "train_journey_snacks": "train_journey_essentials",
    "ganesh_chaturthi_preparation": "ganesh_chaturthi",
}
DB_TO_CATALOG: Dict[str, str] = {v: k for k, v in MISSION_DB_ALIASES.items()}

CONFIDENCE_THRESHOLD = 0.5


class MissionDiscoveryAgent(BaseAgent):
    """Agent 1 – Mission Discovery: intent, detection, requirements, cart, explainability."""

    def __init__(self):
        super().__init__(name="MissionDiscoveryAgent")
        self.detection_service = DetectionService()
        self.mission_repository = MissionRepository()
        self.graph_service = GraphService()

    def execute(self, action: str, payload: Any) -> Any:
        if action == "discover":
            query = payload.get("query", "") if isinstance(payload, dict) else str(payload)
            return self.discover(query)
        raise ValueError(f"Unknown action {action} for MissionDiscoveryAgent")

    def discover(self, query: str) -> Dict[str, Any]:
        detection = self.detection_service.detect_mission(query)
        candidates = self._score_candidates(query)
        intent = self._build_intent(query, detection)
        mission, candidates, detection_reason = self._resolve_detection(detection, candidates)
        requirements = self._map_requirements(mission)
        suggested_cart = self._generate_cart(mission, intent["parameters"], requirements)
        explanation = self._build_explanation(query, intent, mission, candidates, detection_reason)

        return {
            "intent": intent,
            "mission": {
                "detected_mission": mission,
                "confidence": candidates[0]["score"] if candidates else 0.0,
                "candidate_missions": candidates,
            },
            "requirements": requirements,
            "suggested_cart": suggested_cart,
            "explanation": explanation,
        }

    def _build_intent(self, query: str, detection: Dict[str, Any]) -> Dict[str, Any]:
        query_lower = query.lower()
        parameters = detection.get("parameters") if detection.get("success") else None
        if not parameters:
            parameters = self._extract_parameters(query, query_lower, {"guest_count": 1, "audience": "adults"})

        goal = self._infer_goal_from_query(query_lower)
        if detection.get("success") and detection.get("reason"):
            reason_text = str(detection["reason"])
            if len(reason_text) > 5 and "heuristic" not in reason_text.lower():
                goal = reason_text

        entities: List[str] = []
        for mission in self.mission_repository.list_missions():
            if not self.is_approved_mission(mission.mission_id):
                continue
            for kw in mission.keywords:
                if kw.lower() in query_lower and kw.lower() not in entities:
                    entities.append(kw.lower())

        return {"intent": goal, "entities": entities, "parameters": parameters}

    def _infer_goal_from_query(self, query_lower: str) -> str:
        if re.search(r"turning\s*\d+|birthday", query_lower):
            return "birthday celebration"
        if "biryani" in query_lower:
            return "biryani preparation"
        if "exam" in query_lower:
            return "exam preparation"
        if "grocery" in query_lower or "groceries" in query_lower:
            return "grocery shopping"
        if "train" in query_lower:
            return "train journey"
        if "weight" in query_lower and "loss" in query_lower:
            return "weight loss"
        if "housewarming" in query_lower:
            return "housewarming ceremony"
        if "family gathering" in query_lower or ("family" in query_lower and "gathering" in query_lower):
            return "family gathering"
        return "general shopping"

    @staticmethod
    def to_catalog_id(db_mission_id: str) -> str:
        return DB_TO_CATALOG.get(db_mission_id, db_mission_id)

    @staticmethod
    def to_db_id(catalog_mission_id: str) -> str:
        return MISSION_DB_ALIASES.get(catalog_mission_id, catalog_mission_id)

    @staticmethod
    def is_approved_mission(mission_id: str) -> bool:
        catalog_id = MissionDiscoveryAgent.to_catalog_id(mission_id)
        return catalog_id in FROZEN_MISSION_CATALOG

    def _text_match_score(self, query_lower: str, mission: Any) -> float:
        score = 0.0

        for example in mission.intent_examples:
            ex_lower = example.lower()
            if ex_lower in query_lower or query_lower in ex_lower:
                return 0.95
            q_words = set(re.findall(r"\w+", query_lower))
            e_words = set(re.findall(r"\w+", ex_lower))
            if q_words:
                overlap = len(q_words & e_words) / len(q_words)
                if overlap >= 0.45:
                    score = max(score, 0.65 + overlap * 0.25)

        for syn in mission.synonyms:
            if syn.lower() in query_lower:
                score = max(score, 0.88)

        kw_hits = sum(1 for kw in mission.keywords if kw.lower() in query_lower)
        if kw_hits:
            score = max(score, min(0.92, 0.35 + kw_hits * 0.18))

        for part in mission.mission_id.split("_"):
            if len(part) > 3 and re.search(rf"\b{re.escape(part)}\b", query_lower):
                score = max(score, 0.78)

        catalog_id = self.to_catalog_id(mission.mission_id)
        if catalog_id == "birthday_party" and (
            re.search(r"turning\s*\d+", query_lower) or re.search(r"inviting\s+\d+", query_lower)
        ):
            score = max(score, 0.94)
        if catalog_id == "monthly_grocery_refill" and "month" in query_lower and (
            "grocery" in query_lower or "groceries" in query_lower
        ):
            score = max(score, 0.95)
        if catalog_id == "exam_preparation_week" and "exam" in query_lower:
            score = max(score, 0.92)
        if catalog_id == "weight_loss_journey" and ("weight" in query_lower or "losing weight" in query_lower):
            score = max(score, 0.92)
        if catalog_id == "housewarming_ceremony" and "housewarming" in query_lower:
            score = max(score, 0.95)
        if catalog_id == "train_journey_snacks" and "train" in query_lower:
            score = max(score, 0.90)
        if catalog_id == "biryani_preparation" and "biryani" in query_lower:
            score = max(score, 0.93)
        if catalog_id == "family_gathering" and "gathering" in query_lower:
            score = max(score, 0.88)

        return score

    def _keyword_synonym_boost(self, query_lower: str, mission: Any) -> float:
        return self._text_match_score(query_lower, mission) * 0.35

    def _extract_parameters(self, query: str, query_lower: str, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        guest_count = None
        key_match = re.search(r"(?:people|guests|persons|pax|members|count)\s*[:=]\s*(\d+)", query_lower)
        if key_match:
            guest_count = int(key_match.group(1))

        age = None
        turning_match = re.search(r"turning\s*(\d+)", query_lower) or re.search(r"turned\s*(\d+)", query_lower)
        if turning_match:
            age = int(turning_match.group(1))

        if guest_count is None:
            invite_match = re.search(r"inviting\s+(\d+)", query_lower)
            if invite_match:
                guest_count = int(invite_match.group(1))

        if guest_count is None:
            suffix_match = re.search(
                r"(\d+)\s*(?:people|person|guest|children|child|kid|adult|member|pax|friends?)",
                query_lower,
            )
            if suffix_match:
                guest_count = int(suffix_match.group(1))

        if guest_count is None:
            family_match = re.search(r"family\s+of\s+(\d+)", query_lower)
            if family_match:
                guest_count = int(family_match.group(1))

        if guest_count is None:
            num_match = re.findall(r"\b\d+\b", query_lower)
            if num_match:
                candidates_nums = []
                for n_str in num_match:
                    n = int(n_str)
                    if age is not None and n == age:
                        continue
                    if n >= 100:
                        continue
                    candidates_nums.append(n)
                if candidates_nums:
                    guest_count = candidates_nums[0]

        if guest_count is None:
            guest_count = intent_data.get("guest_count", 1)

        audience = intent_data.get("audience", "adults")
        if age is not None:
            audience = "children" if age < 13 else "adults"
        elif "friends" in query_lower:
            audience = "friends"
        elif "children" in query_lower or "kid" in query_lower:
            audience = "children"
        elif "family" in query_lower:
            audience = "family"

        parameters: Dict[str, Any] = {"guest_count": guest_count, "audience": audience}

        date_match = re.search(
            r"(tomorrow|next\s+week|next\s+[a-zA-Z]+|this\s+[a-zA-Z]+|on\s+[a-zA-Z]+|today)",
            query_lower,
        )
        if date_match:
            parameters["event_date"] = date_match.group(1).strip()

        return parameters

    def _score_candidates(self, query: str) -> List[Dict[str, Any]]:
        query_lower = query.lower()
        query_embedding = self.detection_service.bedrock_client.generate_embeddings(query)
        all_missions = self.mission_repository.list_missions()

        scored: List[Tuple[str, float]] = []
        for mission in all_missions:
            if not self.is_approved_mission(mission.mission_id):
                continue
            catalog_id = self.to_catalog_id(mission.mission_id)
            mission_embedding = self.detection_service._get_or_create_mission_embedding(mission)
            semantic = self.detection_service._get_cosine_similarity(query_embedding, mission_embedding)
            text_score = self._text_match_score(query_lower, mission)
            if text_score >= 0.3:
                combined = max(text_score, semantic * 0.35 + text_score * 0.65)
            else:
                combined = semantic * 0.7 + text_score * 0.3
            scored.append((catalog_id, round(min(1.0, combined), 2)))

        scored.sort(key=lambda x: x[1], reverse=True)
        seen = set()
        candidates: List[Dict[str, Any]] = []
        for catalog_id, score in scored:
            if catalog_id in seen:
                continue
            seen.add(catalog_id)
            candidates.append({"mission": catalog_id, "score": score})
            if len(candidates) >= 5:
                break
        return candidates

    def _resolve_detection(
        self, detection: Dict[str, Any], candidates: List[Dict[str, Any]]
    ) -> Tuple[str, List[Dict[str, Any]], str]:
        reason = detection.get("reason", "") if detection.get("success") else ""

        detected_catalog = candidates[0]["mission"] if candidates else "unknown"

        if detection.get("success") and detection.get("mission_id"):
            det_catalog = self.to_catalog_id(detection["mission_id"])
            if self.is_approved_mission(detection["mission_id"]):
                det_score = next((c["score"] for c in candidates if c["mission"] == det_catalog), 0.0)
                top_score = candidates[0]["score"] if candidates else 0.0
                if det_score >= top_score * 0.85 or det_catalog == detected_catalog:
                    detected_catalog = det_catalog
                    if candidates and candidates[0]["mission"] != det_catalog:
                        candidates = sorted(
                            candidates,
                            key=lambda c: (c["mission"] != det_catalog, -c["score"]),
                        )

        if not candidates:
            return detected_catalog, [], reason

        final_confidence = detection.get("confidence", candidates[0]["score"]) if detection.get("success") else candidates[0]["score"]
        if detection.get("success") and self.to_catalog_id(detection.get("mission_id", "")) == detected_catalog:
            final_confidence = max(final_confidence, detection["confidence"])
        else:
            final_confidence = candidates[0]["score"]

        candidates[0] = {"mission": detected_catalog, "score": round(final_confidence, 2)}
        remaining = [c for c in candidates if c["mission"] != detected_catalog]
        candidates = [candidates[0]] + remaining
        candidates = candidates[:5]

        if len(candidates) < 5:
            for catalog_id in sorted(FROZEN_MISSION_CATALOG):
                if not any(c["mission"] == catalog_id for c in candidates):
                    candidates.append({"mission": catalog_id, "score": 0.0})
                if len(candidates) >= 5:
                    break

        return detected_catalog, candidates, reason

    def _map_requirements(self, catalog_mission_id: str) -> Dict[str, List[str]]:
        db_id = self.to_db_id(catalog_mission_id)
        weighted = self.graph_service.get_mission_requirements_weighted(db_id)

        critical: List[str] = []
        important: List[str] = []
        optional: List[str] = []

        for req in weighted:
            product_id = req["product_id"]
            priority = req.get("priority", "IMPORTANT").upper()
            if priority == "CRITICAL":
                critical.append(product_id)
            elif priority == "OPTIONAL" or not req.get("required", True):
                optional.append(product_id)
            else:
                important.append(product_id)

        return {
            "critical_products": critical,
            "important_products": important,
            "optional_products": optional,
        }

    def _generate_cart(
        self,
        catalog_mission_id: str,
        parameters: Dict[str, Any],
        requirements: Dict[str, List[str]],
    ) -> List[Dict[str, Any]]:
        db_id = self.to_db_id(catalog_mission_id)
        guest_count = int(parameters.get("guest_count", 1))
        rules = self.graph_service.get_mission_rules(db_id)
        rules_map = {r["product"].lower(): r["serves_per_unit"] for r in rules}

        cart: List[Dict[str, Any]] = []
        product_lists = (
            requirements.get("critical_products", [])
            + requirements.get("important_products", [])
        )

        for product_id in product_lists:
            product_key = product_id.lower()
            serves = rules_map.get(product_key)
            if serves and serves > 0:
                quantity = max(1, math.ceil(guest_count / serves))
                reason = f"Serves {guest_count} guests"
            else:
                quantity = guest_count if guest_count > 1 else 1
                reason = f"One per guest" if guest_count > 1 else "Standard unit for mission"

            cart.append({"product_id": product_id, "quantity": quantity, "reason": reason})

        return cart

    def _build_explanation(
        self,
        query: str,
        intent: Dict[str, Any],
        detected_mission: str,
        candidates: List[Dict[str, Any]],
        detection_reason: str,
    ) -> List[str]:
        explanation: List[str] = []
        query_lower = query.lower()

        mission = self.mission_repository.get_mission(self.to_db_id(detected_mission))
        if mission:
            for kw in mission.keywords:
                if kw.lower() in query_lower:
                    explanation.append(f"Detected {kw}-related language.")
                    break
            for syn in mission.synonyms:
                if syn.lower() in query_lower:
                    explanation.append(f"Query matches mission synonym '{syn}'.")
                    break

        if intent["parameters"].get("event_date"):
            explanation.append("Detected future event date.")
        if intent["parameters"].get("guest_count", 1) > 1:
            explanation.append(f"Detected guest count ({intent['parameters']['guest_count']}).")
        if intent.get("entities"):
            explanation.append(f"Identified entities: {', '.join(intent['entities'][:5])}.")

        if candidates and candidates[0]["score"] >= CONFIDENCE_THRESHOLD:
            explanation.append("Mission confidence exceeded threshold.")
        elif candidates:
            explanation.append("Mission selected from top semantic match among approved catalog.")

        if detection_reason:
            explanation.append(detection_reason)

        if not explanation:
            explanation.append(f"Mapped query intent '{intent['intent']}' to mission '{detected_mission}'.")

        return explanation
