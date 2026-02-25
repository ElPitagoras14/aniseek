from pydantic import BaseModel, ConfigDict
from starlette import status
from pydantic.alias_generators import to_camel
from typing import Any, Optional


class APIResponse(BaseModel):
    success: bool
    message: str
    payload: Optional[Any] = None
    error_code: Optional[int] = None

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class SuccessResponse(APIResponse):
    success: bool = True


class NotFoundResponse(APIResponse):
    success: bool = False
    error_code: int = status.HTTP_404_NOT_FOUND
    message: str = "Not Found"


class ConflictResponse(APIResponse):
    success: bool = False
    error_code: int = status.HTTP_409_CONFLICT
    message: str = "Conflict"


class BadRequestResponse(APIResponse):
    success: bool = False
    error_code: int = status.HTTP_400_BAD_REQUEST
    message: str = "Bad Request"


class InternalServerErrorResponse(APIResponse):
    success: bool = False
    error_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = "Internal Server Error"


class UnauthorizedResponse(APIResponse):
    success: bool = False
    error_code: int = status.HTTP_401_UNAUTHORIZED
    message: str = "Unauthorized"
