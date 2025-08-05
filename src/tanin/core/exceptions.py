from typing import Optional, List

from tanin.schemas.response_schema import ErrorResponse, ErrorDetail


class APIException(Exception):
    status_code: int = 500
    error: ErrorResponse = ErrorResponse(code="INTERNAL_SERVER_ERROR",
                                         message="An unexpected internal server error occurred.")

    def __init__(
            self,
            status_code: Optional[int] = None,
            code: Optional[str] = None,
            message: Optional[str] = None,
            details: Optional[List[ErrorDetail]] = None,
    ):
        self.status_code = status_code or self.status_code
        self.error = ErrorResponse(
            code=code or self.error.code,
            message=message or self.error.message,
            details=details
        )


class NotFoundException(APIException):
    status_code = 404
    error = ErrorResponse(code="NOT_FOUND", message="The requested resource was not found.")


class UserNotFoundException(NotFoundException):
    error = ErrorResponse(code="USER_NOT_FOUND", message="A user with the given ID was not found.")


class ForbiddenException(APIException):
    status_code = 403
    error = ErrorResponse(code="FORBIDDEN", message="You do not have permission to perform this action.")
