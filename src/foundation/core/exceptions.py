class LifeGraphException(Exception):
    """Base exception for LifeGraph"""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundException(LifeGraphException):
    def __init__(self, entity_name: str, entity_id: str):
        super().__init__(
            message=f"{entity_name} with id {entity_id} not found.",
            code="NOT_FOUND",
            status_code=404
        )

class ValidationException(LifeGraphException):
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400
        )
