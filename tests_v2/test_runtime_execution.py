import os
import pytest
from unittest.mock import MagicMock
from orchestration.master_orchestrator import OutcomeOrchestrator

def test_runtime_execution_live_path():
    # Set to BEDROCK_LIVE mode
    os.environ["MODE"] = "BEDROCK_LIVE"
    try:
        orchestrator = OutcomeOrchestrator()
        orchestrator.ai_gateway.cache.clear()
        
        # Mock the converse call of bedrock runtime client to return valid mock responses
        # so that it simulates successful bedrock calls
        mock_client = MagicMock()
        orchestrator.ai_gateway.bedrock.client = mock_client
        orchestrator.ai_gateway.bedrock.local_mode = False
        
        # Setup mock returns for different agents.
        # When converse is called, we return text content based on the agent name in system/prompt
        def converse_side_effect(modelId, messages, system=None, inferenceConfig=None):
            prompt = messages[0]["content"][0]["text"].lower()
            system_prompt = system[0]["text"].lower() if system else ""
            
            # Simple agent router responses that are JSON serializable and fit schemas
            # 1. Mission Agent
            if "mission" in system_prompt:
                text = '{"original_output": {}, "ai_analysis": {"detected_mission": "weight_loss_journey", "sub_goals": ["fat_loss"], "user_constraints": [], "lifestyle_indicators": []}, "recommended_changes": [], "accepted_changes": [], "rejected_changes": [], "confidence": 0.95, "reasoning": []}'
            # 2. Cart Agent
            elif "cart" in system_prompt:
                text = '{"original_output": {}, "ai_analysis": {"items": [{"product_id": "item1", "title": "Item 1", "priority": "CRITICAL", "reason": "Aligned", "status": "APPROVED", "feedback": null}], "mission_coherence_score": 95}, "recommended_changes": [], "accepted_changes": [], "rejected_changes": [], "confidence": 0.95, "reasoning": []}'
            # 3. Verification Agent
            elif "verification" in system_prompt:
                text = '{"original_output": {}, "ai_analysis": {"readiness_score": 90, "critical_missing": [], "important_missing": [], "recommended_products": []}, "recommended_changes": [], "accepted_changes": [], "rejected_changes": [], "confidence": 0.95, "reasoning": []}'
            # 4. Risk Agent
            elif "risk" in system_prompt:
                text = '{"original_output": {}, "ai_analysis": {"risk_score": 10, "risk_level": "LOW", "risks": []}, "recommended_changes": [], "accepted_changes": [], "rejected_changes": [], "confidence": 0.95, "reasoning": []}'
            # 5. Regret Agent
            elif "regret" in system_prompt:
                text = '{"original_output": {}, "ai_analysis": {"forgotten_items": [], "impact_score": 0}, "recommended_changes": [], "accepted_changes": [], "rejected_changes": [], "confidence": 0.95, "reasoning": []}'
            # 6. Simulation Agent
            elif "simulation" in system_prompt:
                text = '{"original_output": {}, "ai_analysis": {"current_success": 90, "optimized_success": 90, "improvement": 0, "recommended_additions": []}, "recommended_changes": [], "accepted_changes": [], "rejected_changes": [], "confidence": 0.95, "reasoning": []}'
            # 7. Auditor Agent
            elif "auditor" in system_prompt:
                text = '{"original_output": {}, "ai_analysis": {"overall_confidence_score": 0.95, "audit_score": 95, "grounding_score": 95, "consistency_score": 95, "failures": [], "warnings": [], "improvement_suggestions": []}, "recommended_changes": [], "accepted_changes": [], "rejected_changes": [], "confidence": 0.95, "reasoning": []}'
            else:
                text = '{}'
                
            return {
                "output": {
                    "message": {
                        "content": [
                            {"text": text}
                        ]
                    }
                },
                "usage": {
                    "inputTokens": 100,
                    "outputTokens": 100
                }
            }
            
        mock_client.converse.side_effect = converse_side_effect
        
        # Execute the orchestrator
        response = orchestrator.run_outcome_intelligence("I want to lose weight")
        
        # Verify the structure has customer_response and system_diagnostics at root
        assert "customer_response" in response
        assert "system_diagnostics" in response
        assert len(response.keys()) == 2
        
        diagnostics = response["system_diagnostics"]
        ai_runtime = diagnostics["ai_runtime"]
        runtime_truth = diagnostics["runtime_truth"]
        execution_trace = diagnostics["execution_trace"]
        
        # 1. provider == bedrock
        assert ai_runtime["provider"] == "bedrock"
        
        # 2. mode == LIVE
        assert ai_runtime["mode"] == "LIVE"
        
        # 3. bedrock_invocation_confirmed == true
        assert runtime_truth["bedrock_invocation_confirmed"] is True
        
        # 4. fallback_used == false
        assert runtime_truth["fallback_used"] is False
        
        # 5. provider_matches_runtime == true
        assert runtime_truth["provider_matches_runtime"] is True
        
        # 6. execution_trace contains bedrock_provider invocation
        # Find if any element in the execution_trace has component == 'bedrock_provider'
        bedrock_provider_invoked = any(
            t.get("component") == "bedrock_provider" and t.get("invoked") is True
            for t in execution_trace
        )
        assert bedrock_provider_invoked is True
        
        # Verify components in the execution_trace
        master_orchestrator_traced = any(t.get("component") == "master_orchestrator" for t in execution_trace)
        ai_gateway_traced = any(t.get("component") == "ai_gateway" for t in execution_trace)
        model_router_traced = any(t.get("component") == "model_router" for t in execution_trace)
        
        assert master_orchestrator_traced is True
        assert ai_gateway_traced is True
        assert model_router_traced is True

    finally:
        os.environ["MODE"] = "LOCAL_SIMULATION"
