class AppError(Exception):
    status_code: int = 500
    code: str = "INTERNAL_ERROR"

    def __init__(self, message: str, payload: dict | None = None):
        self.message = message
        self.payload = payload
        super().__init__(message)


class NotFoundError(AppError):
    status_code: int = 404
    code: str = "NOT_FOUND"


class BadRequestError(AppError):
    status_code: int = 400
    code: str = "INVALID_REQUEST"


class ExternalServiceError(AppError):
    status_code: int = 502
    code: str = "EXTERNAL_SERVICE_ERROR"


class UnauthorizedError(AppError):
    status_code: int = 401
    code: str = "UNAUTHORIZED"


class ForbiddenError(AppError):
    status_code: int = 403
    code: str = "FORBIDDEN"


class ConflictError(AppError):
    status_code: int = 409
    code: str = "CONFLICT"


class TooManyRequestsError(AppError):
    status_code: int = 429
    code: str = "TOO_MANY_REQUESTS"
