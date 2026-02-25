from fastapi import HTTPException, status


class CustomHTTPException(HTTPException):
    def __init__(self, status_code: int, detail: str, request_id: str = None):
        super().__init__(status_code=status_code, detail=detail)
        self.request_id = request_id


class NotFoundException(CustomHTTPException):
    def __init__(self, detail: str, request_id: str = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            request_id=request_id,
        )


class ConflictException(CustomHTTPException):
    def __init__(self, detail: str, request_id: str = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            request_id=request_id,
        )


class InternalServerErrorException(CustomHTTPException):
    def __init__(self, detail: str, request_id: str = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            request_id=request_id,
        )


class BadRequestException(CustomHTTPException):
    def __init__(self, detail: str, request_id: str = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            request_id=request_id,
        )
