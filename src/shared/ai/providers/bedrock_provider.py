import os
import json
import logging
import boto3
import threading
from typing import Dict, Any, Optional
from botocore.config import Config

logger = logging.getLogger(__name__)

# Global counters for diagnostics endpoint
_failure_count = 0
_fallback_count = 0
_invocation_count = 0
_lock = threading.Lock()

class BedrockProvider:
    @classmethod
    def get_diagnostics_stats(cls):
        global _failure_count, _fallback_count, _invocation_count
        with _lock:
            return {
                "failure_count": _failure_count,
                "fallback_count": _fallback_count,
                "invocation_count": _invocation_count
            }

    def __init__(self):
        self.client = None
        self.region_name = os.environ.get("AWS_REGION", "ap-south-1")
        self.local_mode = True
        self._thread_local = threading.local()
        self.request_invocations = 0
        self.request_bedrock_calls = 0
        self.request_fallbacks = 0
        self.request_bedrock_confirmed = False
        self.request_models = []
        self._initialize_client()

    def reset_request_metrics(self):
        with _lock:
            self.request_invocations = 0
            self.request_bedrock_calls = 0
            self.request_fallbacks = 0
            self.request_bedrock_confirmed = False
            self.request_models = []

    def get_request_stats(self) -> dict:
        with _lock:
            return {
                "invocations": self.request_invocations,
                "bedrock_calls": self.request_bedrock_calls,
                "fallbacks": self.request_fallbacks,
                "bedrock_confirmed": self.request_bedrock_confirmed,
                "models": list(self.request_models)
            }

    @property
    def last_input_tokens(self) -> int:
        return getattr(self._thread_local, "last_input_tokens", 0)

    @last_input_tokens.setter
    def last_input_tokens(self, val: int):
        self._thread_local.last_input_tokens = val

    @property
    def last_output_tokens(self) -> int:
        return getattr(self._thread_local, "last_output_tokens", 0)

    @last_output_tokens.setter
    def last_output_tokens(self, val: int):
        self._thread_local.last_output_tokens = val

    @property
    def last_latency_ms(self) -> int:
        return getattr(self._thread_local, "last_latency_ms", 0)

    @last_latency_ms.setter
    def last_latency_ms(self, val: int):
        self._thread_local.last_latency_ms = val

    @property
    def last_ver_res(self) -> Optional[Any]:
        return getattr(self, "_last_ver_res", None)

    @last_ver_res.setter
    def last_ver_res(self, val: Any):
        self._last_ver_res = val

    @property
    def last_risk_res(self) -> Optional[Any]:
        return getattr(self, "_last_risk_res", None)

    @last_risk_res.setter
    def last_risk_res(self, val: Any):
        self._last_risk_res = val

    @property
    def current_query(self) -> Optional[str]:
        return getattr(self, "_current_query", None)

    @current_query.setter
    def current_query(self, val: str):
        self._current_query = val

    def _initialize_client(self):
        mode = os.environ.get("MODE", "BEDROCK_LIVE")
        logger.info(f"Initializing BedrockProvider. Active execution mode set to: '{mode}'")
        
        if mode == "LOCAL_SIMULATION":
            self.local_mode = True
            logger.info("Starting BedrockProvider in LOCAL_SIMULATION mode directly.")
            return

        try:
            session = boto3.Session()
            credentials = session.get_credentials()
            if credentials is not None:
                # Add adaptive retries configuration to handle throttling automatically
                retry_config = Config(
                    retries={
                        'max_attempts': 10,
                        'mode': 'adaptive'
                    }
                )
                self.client = session.client("bedrock-runtime", region_name=self.region_name, config=retry_config)
                self.local_mode = False
                logger.info(f"AWS Bedrock runtime client successfully initialized in region {self.region_name} with adaptive retries config.")
            else:
                if mode == "BEDROCK_LIVE":
                    raise RuntimeError("No AWS credentials found while in BEDROCK_LIVE mode.")
                logger.warning("No AWS credentials found. Starting in Local Simulation Mode.")
                self.local_mode = True
        except Exception as e:
            if mode == "BEDROCK_LIVE":
                logger.error(f"Failed to initialize AWS Bedrock client in BEDROCK_LIVE mode: {e}")
                raise RuntimeError(f"Failed to initialize AWS Bedrock client in BEDROCK_LIVE mode: {e}")
            logger.warning(f"Failed to initialize AWS Bedrock client: {e}. Starting in Local Simulation Mode.")
            self.local_mode = True

    def test_connection(self) -> bool:
        mode = os.environ.get("MODE", "BEDROCK_LIVE")
        if mode == "LOCAL_SIMULATION":
            self.local_mode = True
            return True
            
        if not self.client:
            if mode == "BEDROCK_LIVE":
                raise RuntimeError("AWS Bedrock client is not initialized in BEDROCK_LIVE mode.")
            self.local_mode = True
            return True

        try:
            messages = [{"role": "user", "content": [{"text": "Hi"}]}]
            self.client.converse(
                modelId="meta.llama3-8b-instruct-v1:0",
                messages=messages,
                inferenceConfig={"maxTokens": 5}
            )
            self.local_mode = False
            return True
        except Exception as e:
            if mode == "BEDROCK_LIVE":
                logger.error(f"AWS Bedrock connection test failed in BEDROCK_LIVE mode: {e}")
                raise RuntimeError(f"AWS Bedrock connection test failed in BEDROCK_LIVE mode: {e}")
            
            logger.warning(f"AWS Bedrock connection test failed: {e}. Switching to Local Simulation Mode.")
            self.local_mode = True
            return True

    def invoke_model(self, model_id: str, prompt: str, system_prompt: Optional[str] = None) -> str:
        global _invocation_count, _failure_count
        with _lock:
            _invocation_count += 1
            self.request_invocations += 1
            if model_id not in self.request_models:
                self.request_models.append(model_id)
        
        mode = os.environ.get("MODE", "BEDROCK_LIVE")
        if mode == "BEDROCK_LIVE":
            if self.local_mode or not self.client:
                raise RuntimeError(f"AWS Bedrock client is not initialized in BEDROCK_LIVE mode.")
        elif self.local_mode or mode == "LOCAL_SIMULATION":
            with _lock:
                self.request_fallbacks += 1
            return self._simulate_response(model_id, prompt, system_prompt)
        
        self.last_input_tokens = 0
        self.last_output_tokens = 0
        self.last_latency_ms = 0
        
        try:
            messages = [{"role": "user", "content": [{"text": prompt}]}]
            system_prompts = [{"text": system_prompt}] if system_prompt else []
            
            import time
            t0 = time.time()
            
            response = self.client.converse(
                modelId=model_id,
                messages=messages,
                system=system_prompts,
                inferenceConfig={
                    "temperature": 0.1,
                    "maxTokens": 2048
                }
            )
            
            latency = (time.time() - t0) * 1000
            self.last_latency_ms = int(latency)
            
            text = response["output"]["message"]["content"][0]["text"]
            
            usage = response.get("usage", {})
            self.last_input_tokens = usage.get("inputTokens", 0)
            self.last_output_tokens = usage.get("outputTokens", 0)
            
            logger.info(f"Successfully invoked live model {model_id} via Converse API. Latency: {self.last_latency_ms}ms, Input: {self.last_input_tokens}, Output: {self.last_output_tokens}")
            
            with _lock:
                self.request_bedrock_calls += 1
                self.request_bedrock_confirmed = True
                if hasattr(self, "execution_trace") and self.execution_trace is not None:
                    self.execution_trace.append({
                        "component": "bedrock_provider",
                        "invoked": True
                    })
            
            return text
        except Exception as e:
            with _lock:
                _failure_count += 1
                self.request_fallbacks += 1
            logger.error(f"Error invoking Bedrock model {model_id}: {e}")
            raise RuntimeError(f"Bedrock invocation failed for model {model_id}: {e}")

    def _simulate_response(self, model_id: str, prompt: str, system_prompt: Optional[str]) -> str:
        """Simulates structured JSON outputs matching the generic DecisionDelta wrapper."""
        global _fallback_count
        with _lock:
            _fallback_count += 1
        
        prompt_lower = prompt.lower()
        
        # 1. Mission Agent Mock Response
        if "mission intelligence agent" in prompt_lower:
            # Extract the actual user query from the rendered prompt (not the template example text)
            import re
            q_match = re.search(r'evaluate the user query:\s*"([^"]*)"', prompt_lower)
            user_query = q_match.group(1) if q_match else ""
            
            detected = "monthly_grocery_refill"
            if "month" in user_query:
                detected = "monthly_grocery_refill"
            elif "week" in user_query or "family of 4" in user_query:
                detected = "weekly_grocery_shopping"
            elif "eating healthy" in user_query or "start eating healthy" in user_query or "start a healthy lifestyle" in user_query:
                detected = "healthy_lifestyle_start"
            elif "lose weight" in user_query or "diet" in user_query:
                detected = "weight_loss_journey"
            elif "cooking session" in user_query or "cooking" in user_query or "biryani" in user_query:
                if "biryani" in user_query:
                    detected = "chicken_biryani"
                else:
                    detected = "weekend_cooking_session"
            
            
            user_constraints = []
            health_conditions = []
            evidence_validation = []
            
            if "diabetic" in user_query or "diabetes" in user_query:
                user_constraints.append("diabetic")
                health_conditions.append("diabetic")
                evidence_validation.append({"constraint": "diabetic", "evidence_source": "query"})
                
            if "weight" in user_query or "diet" in user_query or "healthy" in user_query:
                lifestyle_indicators = ["healthy_eating"]
                evidence_validation.append({"constraint": "healthy_eating", "evidence_source": "query"})
            else:
                lifestyle_indicators = ["general_refill"]
                evidence_validation.append({"constraint": "general_refill", "evidence_source": "query"})
                    
            ai_analysis = {
                "detected_mission": detected,
                "sub_goals": ["reduce_sugar", "fat_loss"] if "weight" in user_query else ["bulk_grocery"],
                "user_constraints": user_constraints,
                "lifestyle_indicators": lifestyle_indicators,
                "health_conditions": health_conditions,
                "evidence_validation": evidence_validation
            }
            
            return json.dumps({
                "original_output": {"detected_mission": detected},
                "ai_analysis": ai_analysis,
                "recommended_changes": [],
                "accepted_changes": [],
                "rejected_changes": [],
                "confidence": 0.95,
                "reasoning": ["Found matching intent, mapped sub-goals and lifestyle tags"]
            })

        # 2. Cart Agent Mock Response
        if "cart intelligence agent" in prompt_lower:
            items_feedback = []
            rejections = []
            
            # Reject high sugar chocolate bar in weight loss
            q_lower = self.current_query.lower() if self.current_query is not None else ""
            if "cadbury" in q_lower or "chocolate" in q_lower:
                items_feedback.append({
                    "product_id": "cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g",
                    "title": "Cadbury Dairy Milk Silk Chocolate Bar, 250g (Pack of 2 x 250g)",
                    "priority": "OPTIONAL",
                    "reason": "Chocolate has high sugar content and is not aligned with weight loss",
                    "status": "REJECTED",
                    "feedback": "Reject high sugar snack"
                })
                rejections.append({
                    "type": "reject_product",
                    "product_id": "cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g",
                    "reason": "Removed due to weight loss sugar restriction"
                })
                coherence = 90
            else:
                items_feedback.append({
                    "product_id": "dummy_product",
                    "title": "Staple Item",
                    "priority": "CRITICAL",
                    "reason": "Correct alignment with mission",
                    "status": "APPROVED",
                    "feedback": None
                })
                coherence = 95
                
            return json.dumps({
                "original_output": {},
                "ai_analysis": {
                    "items": items_feedback,
                    "mission_coherence_score": coherence
                },
                "recommended_changes": rejections,
                "accepted_changes": rejections,
                "rejected_changes": [],
                "confidence": 0.96,
                "reasoning": ["Analyzed cart for sugar/diet matches and safety filters"]
            })

        # 3. Verification Agent Mock Response
        if "verification intelligence agent" in prompt_lower:
            # AI agrees with deterministic readiness score (no override = lower override rate)
            readiness = self.last_ver_res.readiness_score if self.last_ver_res is not None else 78
            
            return json.dumps({
                "original_output": {"readiness_score": readiness},
                "ai_analysis": {
                    "readiness_score": readiness,
                    "critical_missing": [],
                    "important_missing": [],
                    "recommended_products": []
                },
                "recommended_changes": [],
                "accepted_changes": [],
                "rejected_changes": [],
                "confidence": 0.94,
                "reasoning": ["Readiness score confirmed by AI verification"]
            })

        # 4. Risk Agent Mock Response
        if "risk intelligence agent" in prompt_lower:
            # AI agrees with deterministic risk score (no override = lower override rate)
            risk_level = self.last_risk_res.risk_level if self.last_risk_res is not None else "MEDIUM"
            risk_score = self.last_risk_res.risk_score if self.last_risk_res is not None else 35
                
            return json.dumps({
                "original_output": {"risk_level": risk_level, "risk_score": risk_score},
                "ai_analysis": {
                    "risk_score": risk_score,
                    "risk_level": risk_level,
                    "risks": [{"type": "readiness", "severity": risk_level, "reason": "Evaluated based on actual staples missing"}]
                },
                "recommended_changes": [],
                "accepted_changes": [],
                "rejected_changes": [],
                "confidence": 0.95,
                "reasoning": [f"Determined actual risk is {risk_level} based on presence of essential items"]
            })

        # 5. Regret Prevention Agent Mock Response
        if "regret prevention agent" in prompt_lower:
            # Return empty forgotten items to avoid unnecessary overrides
            forgotten = []
                
            return json.dumps({
                "original_output": {"forgotten_items": []},
                "ai_analysis": {
                    "forgotten_items": forgotten,
                    "impact_score": 0
                },
                "recommended_changes": [],
                "accepted_changes": [],
                "rejected_changes": [],
                "confidence": 0.92,
                "reasoning": ["No missing essentials detected that would cause regret"]
            })

        # 6. Simulation Agent Mock Response
        if "simulation agent" in prompt_lower:
            # Return success score aligned with baseline to avoid calibration overrides
            readiness = self.last_ver_res.readiness_score if self.last_ver_res is not None else 78
            risk = self.last_risk_res.risk_score if self.last_risk_res is not None else 35
            baseline_success = int(readiness * 0.7 + (100 - risk) * 0.3)
            opt = min(95, max(0, baseline_success))
            curr = min(95, max(0, readiness))
            
            return json.dumps({
                "original_output": {"current_success": curr, "optimized_success": opt},
                "ai_analysis": {
                    "current_success": curr,
                    "optimized_success": opt,
                    "improvement": max(0, opt - curr),
                    "recommended_additions": []
                },
                "recommended_changes": [],
                "accepted_changes": [],
                "rejected_changes": [],
                "confidence": 0.95,
                "reasoning": ["Estimated success probability matching current readiness and risk profiles"]
            })

        # 7. Auditor Agent Mock Response
        if "outcome auditor agent" in prompt_lower:
            return json.dumps({
                "original_output": {},
                "ai_analysis": {
                    "overall_confidence_score": 0.98,
                    "audit_score": 95,
                    "grounding_score": 100,
                    "consistency_score": 100,
                    "failures": [],
                    "warnings": [],
                    "improvement_suggestions": []
                },
                "recommended_changes": [],
                "accepted_changes": [],
                "rejected_changes": [],
                "confidence": 0.98,
                "reasoning": ["Audit confirms compliant outputs, 0 UUID leaks, and 0 safety conflicts"]
            })

        # Fallback
        return json.dumps({
            "original_output": {},
            "ai_analysis": {"status": "SUCCESS"},
            "recommended_changes": [],
            "accepted_changes": [],
            "rejected_changes": [],
            "confidence": 1.0,
            "reasoning": ["Triggered fallback mock template"]
        })
