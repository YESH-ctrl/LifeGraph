import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class SuccessCalibrator:
    def __init__(self):
        pass

    def calibrate_success_score(
        self,
        readiness_score: int,
        risk_score: int,
        mission_coherence_score: int,
        ai_suggested_success: int
    ) -> Tuple[int, str]:
        """
        Calibrates the success score based on objective parameters.
        Returns: (calibrated_score, explanation)
        """
        # Baseline formula: success is proportional to readiness, reduced by risk factors, and scaled by mission coherence
        baseline_success = readiness_score * 0.7 + (100 - risk_score) * 0.3
        
        # Scale slightly by mission coherence score
        coherence_factor = max(0.5, min(1.0, mission_coherence_score / 100.0))
        baseline_success = baseline_success * coherence_factor
        
        # Cap at 95 (as per simulation service constraints)
        baseline_success = min(95, max(0, int(baseline_success)))

        # Define bounds: AI suggested score must be within +/- 15 points of baseline success
        min_allowed = max(0, baseline_success - 15)
        max_allowed = min(95, baseline_success + 15)

        if ai_suggested_success > max_allowed:
            calibrated_score = max_allowed
            explanation = f"AI success score ({ai_suggested_success}%) exceeded reality constraint cap ({max_allowed}%) based on readiness ({readiness_score}%) and risk ({risk_score}%). Calibrated down."
        elif ai_suggested_success < min_allowed:
            calibrated_score = min_allowed
            explanation = f"AI success score ({ai_suggested_success}%) was below reality constraint floor ({min_allowed}%) based on readiness ({readiness_score}%) and risk ({risk_score}%). Calibrated up."
        else:
            calibrated_score = ai_suggested_success
            explanation = f"AI success score ({ai_suggested_success}%) is grounded within valid bounds (+/- 15% of baseline {baseline_success}%)."

        return calibrated_score, explanation
