import os
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RuntimeTruthEngine:
    def __init__(self):
        pass

    def verify_runtime_truth(self, state: Dict[str, Any], bedrock_provider) -> Dict[str, Any]:
        """
        Verifies actual execution statistics directly from bedrock_provider request stats.
        Never infers the truth from MODE environment variables.
        """
        stats = bedrock_provider.get_request_stats()
        
        bedrock_invocations = stats.get("bedrock_calls", 0)
        fallback_count = stats.get("fallbacks", 0)
        bedrock_confirmed = stats.get("bedrock_confirmed", False)
        
        # Determine actual provider and model used based strictly on actual calls
        if bedrock_confirmed:
            actual_provider = "bedrock"
            # Extract first model ID used, or default to a bedrock model ID
            models = stats.get("models", [])
            actual_model = models[0] if models else "meta.llama3-70b-instruct-v1:0"
        else:
            actual_provider = "simulation"
            actual_model = "local-simulation-model"
            
        actual_mode = "LIVE" if actual_provider == "bedrock" else "SIMULATION"
        
        # Check if the declared provider in state metadata matches actual execution provider
        declared_provider = None
        # Check ai_runtime and ai_metadata
        ai_runtime = state.get("ai_runtime") or {}
        ai_metadata = state.get("ai_metadata") or {}
        declared_provider = ai_runtime.get("provider") or ai_metadata.get("provider")
        
        provider_matches = (declared_provider == actual_provider) if declared_provider else True
        
        # Construct runtime_truth block
        runtime_truth = {
            "bedrock_invocation_confirmed": bedrock_confirmed,
            "provider_matches_runtime": provider_matches,
            "fallback_used": fallback_count > 0,
            "verified_at": datetime.utcnow().isoformat() + "Z"
        }
        
        # Single Source of Truth Rules:
        # If provider=simulation -> live_execution_verified=false
        # If provider=bedrock -> live_execution_verified=true
        live_execution_verified = (actual_provider == "bedrock")
        
        logger.info(
            f"RuntimeTruthEngine verification: provider={actual_provider}, model={actual_model}, "
            f"mode={actual_mode}, confirmed={bedrock_confirmed}, fallbacks={fallback_count}"
        )
        
        return {
            "runtime_truth": runtime_truth,
            "actual_provider": actual_provider,
            "actual_model": actual_model,
            "actual_mode": actual_mode,
            "live_execution_verified": live_execution_verified,
            "bedrock_invocation_count": bedrock_invocations,
            "fallback_count": fallback_count
        }
