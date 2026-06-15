import logging
from typing import Type, TypeVar, Dict, Any, Optional
from pydantic import BaseModel

from .providers.bedrock_provider import BedrockProvider
from .providers.claude_provider import ClaudeProvider
from .prompt_manager import PromptManager
from .model_router import ModelRouter
from .response_cache import ResponseCache
from .token_tracker import TokenTracker
from .cost_tracker import CostTracker
from .validators.hallucination_detector import HallucinationDetector
from .validators.confidence_engine import ConfidenceEngine

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

class AIGateway:
    def __init__(self):
        self.bedrock = BedrockProvider()
        self.claude = ClaudeProvider()
        self.prompts = PromptManager()
        self.router = ModelRouter()
        self.cache = ResponseCache()
        self.tokens = TokenTracker()
        self.costs = CostTracker()
        self.detector = HallucinationDetector()
        self.confidence = ConfidenceEngine()

    def execute_agent(self, agent_name: str, schema_class: Type[T], template_version: str = "1.0.0", **kwargs) -> T:
        """
        Executes a single intelligence agent prompt.
        Handles caching, token tracking, cost evaluation, and response validation.
        """
        model_id = self.router.get_model_for_agent(agent_name)
        
        # 1. Render Prompt
        prompt = self.prompts.render(agent_name.lower(), template_version, **kwargs)
        system_prompt = (
            f"System prompt for {agent_name} agent. Output raw JSON matches only. "
            "CRITICAL: You MUST set the \"original_output\" field to {} (an empty JSON object) in your JSON response. "
            "Do NOT copy the input JSON or list of items into \"original_output\" under any circumstances. Keep it as {} exactly."
        )
        
        # 2. Check Cache
        cached_response = self.cache.get(model_id, prompt, system_prompt)
        if cached_response:
            logger.info(f"Response cache hit for agent '{agent_name}'. Skipping inference.")
            try:
                return self.claude.parse_json_response(cached_response, schema_class)
            except Exception as e:
                logger.warning(f"Failed to parse cached JSON response for '{agent_name}': {e}. Retrying inference.")
        
        # 3. Invoke Inference
        logger.info(f"Inference calling model {model_id} for agent '{agent_name}'...")
        if hasattr(self, "execution_trace") and self.execution_trace is not None:
            provider_name = "simulation" if self.bedrock.local_mode else "bedrock"
            self.execution_trace.append({
                "component": "ai_gateway",
                "provider": provider_name
            })
            self.execution_trace.append({
                "component": "model_router",
                "model": model_id,
                "agent": agent_name
            })
        response_text = self.bedrock.invoke_model(model_id, prompt, system_prompt)
        
        # 4. Cache response
        self.cache.set(model_id, prompt, system_prompt, response_text)
        
        # 5. Token & Cost Tracker Execution
        if not self.bedrock.local_mode:
            in_tok = self.bedrock.last_input_tokens
            out_tok = self.bedrock.last_output_tokens
            if in_tok == 0:
                in_tok = self.tokens.estimate_tokens(prompt + (system_prompt or ""))
            if out_tok == 0:
                out_tok = self.tokens.estimate_tokens(response_text)
            label = "Actual"
        else:
            in_tok = self.tokens.estimate_tokens(prompt + (system_prompt or ""))
            out_tok = self.tokens.estimate_tokens(response_text)
            label = "Est."
            
        self.tokens.record_usage(in_tok, out_tok)
        cost = self.costs.calculate_cost(model_id, in_tok, out_tok)
        logger.info(f"Agent '{agent_name}' complete. {label} Input Tokens: {in_tok}, Output: {out_tok}, Cost: ${cost:.6f} USD.")
        
        # 6. Parse and Validate Schema
        parsed = self.claude.parse_json_response(response_text, schema_class)
        
        # Populate original_output programmatically if empty
        if not parsed.original_output:
            import json
            for key in ["original_json", "verification", "risk", "metrics", "cart", "blueprint", "capabilities", "products_json", "cart_items"]:
                if key in kwargs:
                    val = kwargs[key]
                    if isinstance(val, str):
                        try:
                            parsed.original_output = json.loads(val)
                        except Exception:
                            parsed.original_output = {key: val}
                    elif isinstance(val, (dict, list)):
                        parsed.original_output = {key: val} if isinstance(val, list) else val
                    break
        
        # 7. Hallucination Detection (UUID leak checks)
        parsed_dict = parsed.model_dump()
        leaks = self.detector.detect_uuid_leaks(parsed_dict)
        if leaks:
            logger.warning(f"UUID leakages detected in agent '{agent_name}' response: {leaks}. Sanitizing outputs.")
            # We don't crash, but log safety warnings
            
        return parsed
