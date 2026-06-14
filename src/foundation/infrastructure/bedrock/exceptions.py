from foundation.core.exceptions import LifeGraphException

class BedrockError(LifeGraphException):
    """Base exception for Bedrock operations"""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(
            message=message,
            code="BEDROCK_ERROR",
            status_code=status_code
        )

class BedrockConfigurationError(BedrockError):
    """Exception for Bedrock configuration issues"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=500
        )
        self.code = "BEDROCK_CONFIGURATION_ERROR"

class BedrockInvocationError(BedrockError):
    """Exception for Bedrock model invocation failures"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=502
        )
        self.code = "BEDROCK_INVOCATION_ERROR"
