import json
import logging
import re
from typing import Dict, Any, List, Tuple

from infrastructure.bedrock.client import BedrockClient
from shared.repositories.mission_repository import MissionRepository
from graph.service import GraphService

logger = logging.getLogger(__name__)

# Global cache to store pre-computed mission embeddings to avoid heavy runtime Bedrock billing/latency
_MISSION_EMBEDDINGS_CACHE: Dict[str, List[float]] = {}

class DetectionService:
    def __init__(self):
        self.bedrock_client = BedrockClient()
        self.mission_repository = MissionRepository()
        self.graph_service = GraphService()

    def _get_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculates dot product of two normalized vectors (cosine similarity)."""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        dot_product = sum(x * y for x, y in zip(vec1, vec2))
        return dot_product

    def _get_or_create_mission_embedding(self, mission: Any) -> List[float]:
        """Gets cached embedding for a mission or generates a new one."""
        # Phase 2: Pull pre-computed embedding from DynamoDB if present
        if hasattr(mission, "embedding") and mission.embedding:
            return mission.embedding
            
        mission_id = mission.mission_id
        if mission_id in _MISSION_EMBEDDINGS_CACHE:
            return _MISSION_EMBEDDINGS_CACHE[mission_id]

        # Combine fields into a rich text representative of the mission
        keywords_str = " ".join(mission.keywords)
        synonyms_str = " ".join(mission.synonyms)
        examples_str = " ".join(mission.intent_examples)
        combined_text = f"{mission.name}. {mission.description}. Keywords: {keywords_str}. Synonyms: {synonyms_str}. Examples: {examples_str}"
        
        try:
            embedding = self.bedrock_client.generate_embeddings(combined_text)
            _MISSION_EMBEDDINGS_CACHE[mission_id] = embedding
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding for mission {mission_id}: {e}")
            return [0.0] * 1024

    def detect_mission(self, query: str) -> Dict[str, Any]:
        """
        Executes the Semantic Mission Detection Pipeline:
        1. Bedrock Intent Understanding
        2. Generate query embedding (Phase 3)
        3. Semantic Retrieval (Phase 4: vector-only similarity retrieval, no keyword overlap)
        4. Re-Ranking / Fallback (Phase 5 & 9: Claude re-ranking or Titan + Graph fallback)
        5. Graph Validation Layer (Phase 6: validate candidates loop)
        6. Context Extraction (Phase 7: guest_count, audience, event_date)
        7. Confidence Scoring (Phase 8: weighted combination score)
        """
        logger.info(f"Detecting mission for query: '{query}'")
        query_lower = query.lower()

        # Step 1: Bedrock Intent Understanding (or mock extraction)
        intent_prompt = f"""You are an expert intent extractor for Indian e-commerce.
Analyze the user's shopping intent query: "{query}"

Extract the following details as a JSON object:
- goal: The customer's primary shopping objective (e.g. birthday celebration, diwali prep, weekly grocery).
- event_type: Category of the intent (e.g. festival, event, cooking, grocery, travel, health, student, spiritual).
- guest_count: Estimated number of guests, participants, or people involved (integer, default to 1 if unspecified).
- audience: Primary target audience if specified (e.g. children, adults, family, bachelors).

Return ONLY the valid JSON object, no other explanation or wrapper tags.
"""
        try:
            intent_res = self.bedrock_client.invoke_model(intent_prompt)
            clean_content = intent_res.content.strip()
            if clean_content.startswith("```"):
                lines = clean_content.split("\n")
                if lines[0].startswith("```json") or lines[0].startswith("```"):
                    clean_content = "\n".join(lines[1:-1]).strip()
            intent_data = json.loads(clean_content)
        except Exception as e:
            logger.error(f"Step 1 (Intent Understanding) failed: {e}")
            intent_data = {"goal": "general shopping", "guest_count": 1, "event_type": "grocery", "audience": "adults"}

        # --- Phase 7: Context Parameter Extraction ---
        # Extract guest count
        guest_count = None
        key_match = re.search(r'(?:people|guests|persons|pax|members|count)\s*[:=]\s*(\d+)', query_lower)
        if key_match:
            guest_count = int(key_match.group(1))
        
        # Check turning age to avoid misinterpreting it as guest count
        age = None
        turning_match = re.search(r'turning\s*(\d+)', query_lower) or re.search(r'turned\s*(\d+)', query_lower)
        if turning_match:
            age = int(turning_match.group(1))

        if guest_count is None:
            suffix_match = re.search(r'(\d+)\s*(?:people|person|guest|children|child|kid|adult|member|pax)', query_lower)
            if suffix_match:
                guest_count = int(suffix_match.group(1))

        if guest_count is None:
            num_match = re.findall(r'\b\d+\b', query_lower)
            if num_match:
                candidates_nums = []
                for n_str in num_match:
                    n = int(n_str)
                    if age is not None and n == age:
                        continue
                    if n >= 100:  # Skip typical budget values
                        continue
                    candidates_nums.append(n)
                if candidates_nums:
                    guest_count = candidates_nums[0]

        if guest_count is None:
            guest_count = intent_data.get("guest_count", 1)

        # Extract audience
        audience = "adults"
        if age is not None:
            audience = "children" if age < 13 else "adults"
        elif "children" in query_lower or "kid" in query_lower or "child" in query_lower or "kids" in query_lower:
            audience = "children"
        else:
            audience = intent_data.get("audience", "adults")

        # Extract event date (Phase 7)
        event_date = None
        date_match = re.search(r'(tomorrow|next\s+[a-zA-Z]+|this\s+[a-zA-Z]+|on\s+[a-zA-Z]+|today)', query_lower)
        if date_match:
            event_date = date_match.group(1).strip()

        parameters = {
            "guest_count": guest_count,
            "audience": audience
        }
        if event_date:
            parameters["event_date"] = event_date

        # --- Phase 3: User Intent Embedding ---
        query_embedding = self.bedrock_client.generate_embeddings(query)

        # --- Phase 4: Semantic Mission Retrieval (top 10 by pure cosine similarity) ---
        all_missions = self.mission_repository.list_missions()
        if not all_missions:
            return {
                "success": False,
                "error": "No missions found in library. Run seeder first."
            }

        candidates_with_score: List[Tuple[Any, float]] = []
        for mission in all_missions:
            mission_embedding = self._get_or_create_mission_embedding(mission)
            score = self._get_cosine_similarity(query_embedding, mission_embedding)
            candidates_with_score.append((mission, score))

        # Sort descending by pure cosine similarity
        candidates_with_score.sort(key=lambda x: x[1], reverse=True)
        top_candidates = candidates_with_score[:10]

        # --- Phase 5 & 9: Bedrock Re-Ranking / Fallback Layer ---
        nova_available = self.bedrock_client.check_nova_available()
        selected_id = None
        llm_confidence = 0.85 # Fallback LLM confidence
        rerank_reason = "Bypassed LLM re-ranking due to Nova unavailability (Phase 9 fallback)."

        if nova_available:
            candidate_list_str = "\n".join([
                f"- mission_id: \"{m.mission_id}\", name: \"{m.name}\", description: \"{m.description}\""
                for m, _ in top_candidates
            ])

            rerank_prompt = f"""You are a mission classification engine.
User Query: "{query}"
Extracted Goal: "{intent_data.get('goal')}"

Candidate Missions:
{candidate_list_str}

Choose the single best match from the Candidate list above.
Apply these rules strictly:
1. If the User Query specifically mentions a specific festival name (such as "Ganesh Chaturthi", "Diwali", "Holi", "Eid", "Christmas"), prioritize matching that specific festival mission (e.g., ganesh_chaturthi) over more general spiritual/pooja or event missions (e.g., ganesh_pooja).
2. If the User Query specifically mentions a specific product, activity, or transport type (like "biryani", "train", "samosa", "laundry"), prioritize the specific mission centered around that item/activity (e.g., biryani_preparation, train_journey_essentials, samosa_chai_evening, home_laundry_day) rather than broader event, vacation, or category packages (like eid_celebration or family_vacation_pack).

Return ONLY a valid JSON object containing exactly these fields:
- mission_id: The exact mission_id of the chosen candidate.
- confidence: A confidence score between 0.0 and 1.0.
- reason: A concise explanation of why this mission matches the query.

Ensure that all string values in the JSON (especially the "reason" field) do not contain unescaped double quotes or invalid control characters. Do not include any markdown boxes, code blocks, or extra text.
"""
            try:
                rerank_res = self.bedrock_client.invoke_model(rerank_prompt, model_id="amazon.nova-lite-v1:0")
                clean_content = rerank_res.content.strip()
                if clean_content.startswith("```"):
                    lines = clean_content.split("\n")
                    if lines[0].startswith("```json") or lines[0].startswith("```"):
                        clean_content = "\n".join(lines[1:-1]).strip()
                
                # Robust parsing block
                rerank_data = {}
                try:
                    rerank_data = json.loads(clean_content)
                except Exception as json_err:
                    logger.warning(f"Direct JSON loads failed: {json_err}. Trying regex extraction on content: {clean_content}")
                    m_id_match = re.search(r'"mission_id"\s*:\s*"([^"]+)"', clean_content)
                    conf_match = re.search(r'"confidence"\s*:\s*([\d\.]+)', clean_content)
                    reason_match = re.search(r'"reason"\s*:\s*"(.*)"', clean_content, re.DOTALL)
                    if m_id_match:
                        rerank_data["mission_id"] = m_id_match.group(1)
                    if conf_match:
                        rerank_data["confidence"] = float(conf_match.group(1))
                    if reason_match:
                        reason_val = reason_match.group(1).strip()
                        # Strip trailing braces/whitespace if regex grabbed too much
                        if reason_val.endswith('"'):
                            reason_val = reason_val[:-1]
                        if reason_val.endswith('}') or reason_val.endswith('}\n'):
                            idx_brace = reason_val.rfind('"')
                            if idx_brace != -1:
                                reason_val = reason_val[:idx_brace]
                        rerank_data["reason"] = reason_val
                
                selected_id = rerank_data.get("mission_id")
                llm_confidence = float(rerank_data.get("confidence", 0.95))
                rerank_reason = rerank_data.get("reason", "")
            except Exception as e:
                logger.error(f"Re-Ranking failed: {e}. Falling back to Phase 9 mode.")
                selected_id = None

        # Build candidate ranked search order list
        ranked_missions = []
        if selected_id:
            # Place Nova selected candidate first
            chosen_tuple = None
            for m, sim in top_candidates:
                if m.mission_id == selected_id:
                    chosen_tuple = (m, sim)
                    break
            if chosen_tuple:
                ranked_missions.append(chosen_tuple)
                for item in top_candidates:
                    if item[0].mission_id != selected_id:
                        ranked_missions.append(item)
            else:
                ranked_missions = top_candidates
        else:
            ranked_missions = top_candidates

        # --- Phase 6: Graph Validation Layer loop ---
        validated_mission = None
        final_similarity = 0.0
        requirements = []

        for m, sim in ranked_missions:
            db_m = self.mission_repository.get_mission(m.mission_id)
            if db_m:
                reqs = self.graph_service.get_mission_requirements(m.mission_id)
                # Verify required products exist and has relations
                if reqs and len(reqs) > 0:
                    validated_mission = db_m
                    final_similarity = sim
                    requirements = reqs
                    break

        if not validated_mission:
            # Complete validation fallback to first candidate
            validated_mission = top_candidates[0][0]
            final_similarity = top_candidates[0][1]
            requirements = self.graph_service.get_mission_requirements(validated_mission.mission_id)

        # --- Phase 8: Confidence Scoring ---
        semantic_similarity = final_similarity
        graph_score = 1.0 if (requirements and len(requirements) > 0) else 0.0
        
        final_confidence = (
            (semantic_similarity * 0.60)
            + (llm_confidence * 0.25)
            + (graph_score * 0.15)
        )
        final_confidence = round(final_confidence, 2)

        return {
            "success": True,
            "mission_id": validated_mission.mission_id,
            "confidence": final_confidence,
            "reason": rerank_reason,
            "parameters": parameters,
            "validation": {
                "exists": True,
                "graph_complete": graph_score > 0,
                "required_products_count": len(requirements)
            }
        }

    def get_debug_diagnostics(self) -> Dict[str, Any]:
        """Provides diagnostic information about Bedrock model access and state."""
        nova_ok = self.bedrock_client.check_nova_available()
        claude_ok = self.bedrock_client.check_claude_available()
        
        available = []
        if nova_ok:
            available.append("amazon.nova-lite-v1:0")
            available.append("amazon.nova-pro-v1:0")
        if claude_ok:
            available.append("anthropic.claude-3-sonnet-20240229-v1:0")
            
        titan_ok = False
        if not self.bedrock_client.use_mock and self.bedrock_client.client:
            try:
                body = json.dumps({"inputText": "test"})
                self.bedrock_client.client.invoke_model(
                    modelId="amazon.titan-embed-text-v2:0",
                    contentType="application/json",
                    accept="application/json",
                    body=body
                )
                titan_ok = True
                available.append("amazon.titan-embed-text-v2:0")
            except Exception:
                pass
                
        embedding_model = "amazon.titan-embed-text-v2:0" if titan_ok else "mock-embeddings"
        reranker_model = "amazon.nova-lite-v1:0" if nova_ok else "mock-reranker"
        
        return {
            "available_models": available,
            "embedding_model": embedding_model,
            "reranker_model": reranker_model,
            "fallback_mode": not nova_ok
        }
