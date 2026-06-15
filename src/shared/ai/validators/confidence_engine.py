from typing import List, Dict, Any

class ConfidenceEngine:
    def evaluate_mission_confidence(self, matched_kws: List[str], text_length: int) -> float:
        """Computes a confidence score for mission routing."""
        if not matched_kws:
            return 0.5
        
        # Base confidence increases with keywords matched
        base = 0.7 + (min(len(matched_kws), 3) * 0.1)
        # Sligthly penalize long queries with sparse matches
        if text_length > 100:
            base -= 0.05
        return min(1.0, max(0.1, base))

    def evaluate_cart_confidence(self, items_count: int, coherence_score: int) -> float:
        """Computes confidence in generated carts."""
        if items_count == 0:
            return 0.1
        
        coherence_factor = coherence_score / 100.0
        # Cart with >= 8 products gets full size score
        size_factor = min(items_count, 8) / 8.0
        
        confidence = (coherence_factor * 0.7) + (size_factor * 0.3)
        return min(1.0, max(0.1, confidence))
