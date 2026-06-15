class ModelRouter:
    # Verified active Meta Llama 3 models on this AWS account
    SONNET = "meta.llama3-70b-instruct-v1:0"  # Large / complex agent tasks
    HAIKU = "meta.llama3-8b-instruct-v1:0"    # Fast / simple agent tasks

    # Reference Claude constants for account documentation
    # CLAUDE_SONNET = "apac.anthropic.claude-3-5-sonnet-20241022-v2:0" (restricted)
    # CLAUDE_HAIKU = "us.anthropic.claude-3-haiku-20240307-v1:0" (restricted)

    # Default mappings
    ROUTING_MAP = {
        "mission": HAIKU,
        "cart": SONNET,
        "verification": HAIKU,
        "risk": HAIKU,
        "regret": HAIKU,
        "simulation": SONNET,
        "auditor": SONNET
    }

    def get_model_for_agent(self, agent_name: str) -> str:
        return self.ROUTING_MAP.get(agent_name.lower(), self.SONNET)
