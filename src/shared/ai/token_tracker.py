class TokenTracker:
    def __init__(self):
        self._total_input_tokens = 0
        self._total_output_tokens = 0

    def estimate_tokens(self, text: str) -> int:
        """Simple heuristic: ~4 characters per token as a backup tracker."""
        if not text:
            return 0
        return max(1, len(text) // 4)

    def record_usage(self, input_tokens: int, output_tokens: int):
        self._total_input_tokens += input_tokens
        self._total_output_tokens += output_tokens

    @property
    def total_input_tokens(self) -> int:
        return self._total_input_tokens

    @property
    def total_output_tokens(self) -> int:
        return self._total_output_tokens

    def reset(self):
        self._total_input_tokens = 0
        self._total_output_tokens = 0
