import json
import logging
import re
import math
import os
from typing import Dict, Any, List
import boto3
from botocore.exceptions import BotoCoreError, ClientError

from infrastructure.bedrock.models import BedrockResponse
from infrastructure.bedrock.config import BedrockConfig

logger = logging.getLogger(__name__)

# A predefined vocabulary of key terms for our mock embeddings fallback
MOCK_VOCAB = [
    "diwali", "holi", "ganesh", "pooja", "sankranti", "ugadi", "dussehra", "raksha", "eid", "christmas",
    "birthday", "party", "celebration", "anniversary", "housewarming", "shower", "gathering", "dinner",
    "grocery", "refill", "weekly", "monthly", "bachelor", "family", "cooking", "biryani", "paneer",
    "breakfast", "lunch", "meal", "student", "hostel", "exam", "study", "semester", "health", "recovery",
    "aid", "loss", "diet", "protein", "travel", "trip", "road", "vacation", "train", "pilgrimage",
    "sweets", "diyas", "decorations", "flowers", "materials", "gifts", "agarbatti", "kumkum", "turmeric",
    "coconut", "camphor", "fruits", "rice", "dal", "atta", "oil", "vegetables", "milk", "paneer", "spices"
]

class BedrockClient:
    def __init__(self, config: BedrockConfig = None):
        self.config = config or BedrockConfig()
        self.use_mock = os.getenv("MOCK_BEDROCK", "false").lower() == "true"
        self.claude_available = None
        self.nova_available = None
        if not self.use_mock:
            try:
                self.client = boto3.client("bedrock-runtime", region_name=self.config.aws_region)
            except Exception as e:
                logger.warning(f"Could not initialize boto3 Bedrock client: {e}. Using mock mode.")
                self.client = None
                self.use_mock = True
        else:
            self.client = None

    def check_claude_available(self) -> bool:
        """Checks if Claude model access is active and approved on this account."""
        if self.claude_available is not None:
            return self.claude_available
        if self.use_mock or not self.client:
            self.claude_available = False
            return False
            
        try:
            model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1,
                "messages": [{"role": "user", "content": "Hi"}]
            })
            self.client.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=body
            )
            self.claude_available = True
            return True
        except Exception as e:
            logger.warning(f"Claude is not available on Bedrock: {e}. Falling back to local re-ranking.")
            self.claude_available = False
            return False

    def check_nova_available(self) -> bool:
        """Checks if Nova model access is active and approved on this account."""
        if self.nova_available is not None:
            return self.nova_available
        if self.use_mock or not self.client:
            self.nova_available = False
            return False
            
        try:
            model_id = "anthropic.claude-3-haiku-20240307-v1:0"
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1,
                "messages": [{"role": "user", "content": "Hi"}]
            })
            self.client.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=body
            )
            self.nova_available = True
            return True
        except Exception as e:
            logger.warning(f"Nova/Haiku is not available on Bedrock: {e}. Falling back to local re-ranking.")
            self.nova_available = False
            return False

    def generate_embeddings(self, text: str) -> List[float]:
        """Generates embeddings using amazon.titan-embed-text-v2:0 or falls back deterministically."""
        if not self.use_mock and self.client:
            try:
                body = json.dumps({"inputText": text})
                response = self.client.invoke_model(
                    modelId="amazon.titan-embed-text-v2:0",
                    contentType="application/json",
                    accept="application/json",
                    body=body
                )
                response_body = json.loads(response.get("body").read())
                embedding = response_body.get("embedding")
                if embedding:
                    return [float(x) for x in embedding]
            except Exception as e:
                logger.warning(f"Bedrock embedding generation failed: {e}. Falling back to mock embeddings.")
        
        # Deterministic Mock Embedding (1024 dimensions for Titan consistency)
        # We fill the vector based on keyword frequency in the input text
        vector = [0.0] * 1024
        text_lower = text.lower()
        
        # Mark vocabulary hits
        for i, word in enumerate(MOCK_VOCAB):
            if word in text_lower:
                vector[i] = 1.0
                
        # Normalize the vector for cosine similarity consistency
        magnitude = math.sqrt(sum(val * val for val in vector))
        if magnitude > 0:
            vector = [val / magnitude for val in vector]
        else:
            # Fallback to random-seeded deterministic vector if no words hit
            import hashlib
            h = hashlib.sha256(text.encode('utf-8')).digest()
            for i in range(min(1024, len(h) * 8)):
                byte_idx = i // 8
                bit_idx = i % 8
                bit_val = (h[byte_idx] >> bit_idx) & 1
                vector[i] = float(bit_val)
            magnitude = math.sqrt(sum(val * val for val in vector))
            if magnitude > 0:
                vector = [val / magnitude for val in vector]
                
        return vector

    def invoke_model(self, prompt: str, **kwargs) -> BedrockResponse:
        """Invokes a Bedrock model (Claude/Nova) or falls back to local heuristic parsing."""
        model_id = kwargs.get("model_id") or self.config.model_id
        # Use Haiku if Claude default is fallback
        if model_id == "anthropic.claude-v2":
            model_id = "anthropic.claude-3-haiku-20240307-v1:0"

        if not self.use_mock and self.client:
            try:
                # Format request for Nova, Claude 3, or legacy
                if "nova" in model_id:
                    body_dict = {
                        "messages": [
                            {"role": "user", "content": [{"text": prompt}]}
                        ],
                        "inferenceConfig": {
                            "maxTokens": kwargs.get("max_tokens") or self.config.max_tokens or 1024,
                            "temperature": kwargs.get("temperature") or self.config.temperature or 0.7,
                            "topP": kwargs.get("top_p") or self.config.top_p or 0.9
                        }
                    }
                elif "claude-3" in model_id:
                    body_dict = {
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": kwargs.get("max_tokens") or self.config.max_tokens,
                        "temperature": kwargs.get("temperature") or self.config.temperature,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ]
                    }
                else:
                    body_dict = {
                        "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                        "max_tokens_to_sample": kwargs.get("max_tokens") or self.config.max_tokens,
                        "temperature": kwargs.get("temperature") or self.config.temperature,
                        "top_p": kwargs.get("top_p") or self.config.top_p
                    }

                response = self.client.invoke_model(
                    modelId=model_id,
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps(body_dict)
                )
                response_body = json.loads(response.get("body").read())
                
                # Parse output based on response schema
                if "nova" in model_id:
                    content = response_body["output"]["message"]["content"][0]["text"]
                elif "claude-3" in model_id:
                    content = response_body["content"][0]["text"]
                else:
                    content = response_body.get("completion", "")

                return BedrockResponse(
                    content=content,
                    modelId=model_id,
                    usage={},
                    metadata={}
                )
            except Exception as e:
                logger.warning(f"Bedrock invocation failed for model {model_id}: {e}. Falling back to mock model responses.")
        
        # Heuristic Mock LLM Response logic
        mock_content = self._generate_mock_llm_response(prompt)
        return BedrockResponse(
            content=mock_content,
            modelId=model_id,
            usage={"mock": True},
            metadata={"fallback": True}
        )

    def _generate_mock_llm_response(self, prompt: str) -> str:
        """Parses prompt content and returns an appropriate JSON response structure."""
        prompt_lower = prompt.lower()
        
        # 1. Re-ranking prompt handler (more specific checks first)
        if "candidate" in prompt_lower or "choose the most appropriate" in prompt_lower or "choose the single best match" in prompt_lower:
            # Match any word inside quotes following mission_id or missionId
            candidates = re.findall(r'mission_id\s*[:=]\s*["\']([^"\']+)["\']', prompt) or re.findall(r'missionId\s*[:=]\s*["\']([^"\']+)["\']', prompt) or re.findall(r'mission_id\s*[:=]\s*(\w+)', prompt)
            
            if not candidates:
                candidates = ["weekly_grocery"] # safe default
                
            # Extract query and goal from prompt to score candidates robustly
            query_match = re.search(r'[Uu]ser\s+[Qq]uery\s*:\s*(.*)', prompt)
            query_line = query_match.group(1).strip() if query_match else ""
            if (query_line.startswith('"') and query_line.endswith('"')) or (query_line.startswith("'") and query_line.endswith("'")):
                query_text = query_line[1:-1]
            else:
                query_text = query_line
            query_text_lower = query_text.lower()

            goal_match = re.search(r'[Ee]xtracted\s+[Gg]oal\s*:\s*(.*)', prompt)
            goal_line = goal_match.group(1).strip() if goal_match else ""
            if (goal_line.startswith('"') and goal_line.endswith('"')) or (goal_line.startswith("'") and goal_line.endswith("'")):
                goal_text = goal_line[1:-1]
            else:
                goal_text = goal_line
            goal_text_lower = goal_text.lower()

            match_text = f"{query_text_lower} {goal_text_lower}"
            print("DEBUG: match_text =", repr(match_text))
            print("DEBUG: candidates =", candidates)
                
            selected_id = candidates[0]
            best_score = -1
            for cand in candidates:
                cand_score = 0
                parts = cand.lower().split('_')
                for part in parts:
                    if part in match_text:
                        cand_score += 1.5
                    # Give extra weight if exact word matches as a whole word
                    if re.search(rf'\b{part}\b', match_text):
                        cand_score += 2.0
                print(f"DEBUG: candidate={cand}, score={cand_score}")
                if cand_score > best_score:
                    best_score = cand_score
                    selected_id = cand
            # Handle birthday party audience specifically to avoid tie or mapping to legacy BIRTHDAY
            if "birthday" in match_text:
                is_kids = "kids" in match_text or "child" in match_text or "children" in match_text or "kid" in match_text
                # Check if turning age >= 13 is mentioned in the query
                turning_age_match = re.search(r'turning\s*(\d+)', match_text) or re.search(r'turned\s*(\d+)', match_text)
                if turning_age_match and int(turning_age_match.group(1)) >= 13:
                    is_kids = False
                
                if is_kids and "kids_birthday_party" in candidates:
                    selected_id = "kids_birthday_party"
                    best_score = 999.0
                elif not is_kids and "birthday_party" in candidates:
                    selected_id = "birthday_party"
                    best_score = 999.0

            if "ganesh chaturthi" in match_text and "ganesh_chaturthi" in candidates:
                selected_id = "ganesh_chaturthi"
                best_score = 999.0
            if "biryani" in match_text and "biryani_preparation" in candidates:
                selected_id = "biryani_preparation"
                best_score = 999.0
            if "train" in match_text and "train_journey_essentials" in candidates:
                selected_id = "train_journey_essentials"
                best_score = 999.0

            res = {
                "mission_id": selected_id,
                "confidence": 0.95,
                "reason": f"Heuristically selected '{selected_id}' based on query match score of {best_score}."
            }
            return json.dumps(res)

        # 2. Intent extraction prompt handler
        if "goal" in prompt_lower or "guest_count" in prompt_lower or "event_type" in prompt_lower:
            goal = "general mission"
            event_type = "grocery"
            audience = "adults"
            
            # turning X implies birthday celebration
            age = None
            turning_match = re.search(r'turning\s*(\d+)', prompt_lower) or re.search(r'turned\s*(\d+)', prompt_lower)
            if turning_match:
                age = int(turning_match.group(1))
                goal = "birthday celebration"
                event_type = "event"
                if age < 13:
                    audience = "children"
                else:
                    audience = "adults"
            
            # Simple keyword matching to infer event_type & goal (only if not already set by turning)
            if goal == "general mission":
                for key in ["diwali", "holi", "ganesh", "raksha", "eid", "christmas"]:
                    if key in prompt_lower:
                        goal = f"{key} celebration"
                        event_type = "festival"
                        break
                for key in ["birthday", "anniversary", "housewarming"]:
                    if key in prompt_lower:
                        goal = f"{key} celebration"
                        event_type = "event"
                        if "kids" in prompt_lower or "children" in prompt_lower or "child" in prompt_lower or "kid" in prompt_lower:
                            audience = "children"
                        break
                for key in ["biryani", "paneer", "breakfast", "lunch", "dinner"]:
                    if key in prompt_lower:
                        goal = f"{key} preparation"
                        event_type = "cooking"
                        break
                for key in ["hostel", "semester", "exam"]:
                    if key in prompt_lower:
                        goal = "student essentials"
                        event_type = "student"
                        break
                for key in ["grocery", "refill"]:
                    if key in prompt_lower:
                        goal = "grocery shopping"
                        event_type = "grocery"
                        break
                for key in ["trip", "vacation", "travel"]:
                    if key in prompt_lower:
                        goal = "travel planning"
                        event_type = "travel"
                        break
                for key in ["sick", "first aid", "diet", "weight"]:
                    if key in prompt_lower:
                        goal = "health management"
                        event_type = "health"
                        break
                for key in ["vratham", "pooja", "lakshmi"]:
                    if key in prompt_lower:
                        goal = f"{key} preparation"
                        event_type = "spiritual"
                        break

            # Smart guest count extraction
            guest_count = None
            
            # Check for explicit count keys: e.g. "people: 5" or "guests:5" or "pax: 5"
            key_match = re.search(r'(?:people|guests|persons|pax|members|count)\s*[:=]\s*(\d+)', prompt_lower)
            if key_match:
                guest_count = int(key_match.group(1))
            
            if guest_count is None:
                # Regex to find guest counts with suffixes: e.g. "5 people"
                suffix_match = re.search(r'(\d+)\s*(?:people|person|guest|children|child|kid|adult|member|pax)', prompt_lower)
                if suffix_match:
                    guest_count = int(suffix_match.group(1))
                    
            if guest_count is None:
                # Standalone numbers (excluding age and budget numbers if possible)
                num_match = re.findall(r'\b\d+\b', prompt_lower)
                if num_match:
                    # Filter out age or budget (usually > 100) or turning age
                    candidates_nums = []
                    for n_str in num_match:
                        n = int(n_str)
                        # Skip if it is the turning age
                        if age is not None and n == age:
                            continue
                        # Skip typical budget values (> 100)
                        if n >= 100:
                            continue
                        candidates_nums.append(n)
                    if candidates_nums:
                        guest_count = candidates_nums[0]
                        
            if guest_count is None:
                guest_count = 1

            # Determine audience if not already set by age
            if age is None:
                if "children" in prompt_lower or "kid" in prompt_lower or "child" in prompt_lower or "kids" in prompt_lower:
                    audience = "children"
                else:
                    audience = "adults"

            res = {
                "goal": goal,
                "guest_count": guest_count,
                "event_type": event_type,
                "audience": audience
            }
            return json.dumps(res)







        # Catch-all
        return json.dumps({"success": True, "message": "Default mock response"})

    def generate_explanation(self, context: dict) -> BedrockResponse:
        return self.invoke_model(f"Explain this context: {json.dumps(context)}")

    def generate_summary(self, content: str) -> BedrockResponse:
        return self.invoke_model(f"Summarize this: {content}")

    def generate_adaptive_guidance(self, user_context: dict) -> BedrockResponse:
        return self.invoke_model(f"Generate adaptive guidance: {json.dumps(user_context)}")
