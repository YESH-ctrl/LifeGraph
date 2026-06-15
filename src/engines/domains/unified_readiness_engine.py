class UnifiedReadinessEngine:
    def calculate_readiness(self, capability_completion: float, group_completion: float, diversity_score: float) -> int:
        """
        Calculates unified readiness score using the formula:
        readiness_score = 0.5 * capability_completion + 0.3 * group_completion + 0.2 * diversity_score
        Returns an integer rounded to the nearest value, bounded [0, 100].
        """
        score = (0.5 * capability_completion) + (0.3 * group_completion) + (0.2 * diversity_score)
        return min(100, max(0, int(round(score))))
