class ServiceError(Exception):
    """Base class for downstream service failures."""

    def __init__(self, message: str, *, user_message: str | None = None):
        super().__init__(message)
        self.user_message = user_message or message


class ServiceUnavailableError(ServiceError):
    pass


class ServiceForbiddenError(ServiceError):
    pass


class ServiceNotFoundError(ServiceError):
    pass
