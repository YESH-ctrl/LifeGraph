class CostTracker:
    # Pricing per token in USD
    PRICING = {
        "anthropic.claude-3-sonnet": {
            "input": 0.000003,
            "output": 0.000015
        },
        "anthropic.claude-3-haiku": {
            "input": 0.00000025,
            "output": 0.00000125
        },
        "meta.llama3-8b-instruct-v1:0": {
            "input": 0.0000003,
            "output": 0.0000006
        },
        "meta.llama3-70b-instruct-v1:0": {
            "input": 0.00000265,
            "output": 0.0000035
        },
        "default": {
            "input": 0.000001,
            "output": 0.000005
        }
    }

    def __init__(self):
        self._total_cost_usd = 0.0

    def calculate_cost(self, model_id: str, input_tokens: int, output_tokens: int) -> float:
        model_pricing = self.PRICING.get(model_id, self.PRICING["default"])
        cost = (input_tokens * model_pricing["input"]) + (output_tokens * model_pricing["output"])
        self._total_cost_usd += cost
        return cost

    @property
    def total_cost_usd(self) -> float:
        return self._total_cost_usd

    def reset(self):
        self._total_cost_usd = 0.0
