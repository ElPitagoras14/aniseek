class AppError(Exception):
    status_code: int = 500
    code: str = "ERROR_INTERNO"

    def __init__(self, message: str, payload: dict | None = None):
        self.message = message
        self.payload = payload
        super().__init__(message)


class NotFoundError(AppError):
    status_code: int = 404
    code: str = "NO_ENCONTRADO"


class BadRequestError(AppError):
    status_code: int = 400
    code: str = "SOLICITUD_INVALIDA"


class ExternalServiceError(AppError):
    status_code: int = 502
    code: str = "ERROR_SERVICIO_EXTERNO"


class UnauthorizedError(AppError):
    status_code: int = 401
    code: str = "NO_AUTORIZADO"


class ForbiddenError(AppError):
    status_code: int = 403
    code: str = "PROHIBIDO"


class ConflictError(AppError):
    status_code: int = 409
    code: str = "CONFLICTO"
