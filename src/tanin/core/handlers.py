from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from tanin.core.exceptions import APIException
from tanin.schemas.response_schema import ModelResponse, ErrorDetail, ErrorResponse


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    error_response = ModelResponse(
        success=False,
        error=exc.error
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(exclude_none=True)
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = [
        ErrorDetail(loc=[str(loc) for loc in err['loc']], msg=err['msg'], type=err['type'])
        for err in exc.errors()
    ]

    error_payload = ErrorResponse(
        code="VALIDATION_ERROR",
        message="Input validation failed.",
        details=details
    )

    error_response = ModelResponse(
        success=False,
        error=error_payload
    )

    return JSONResponse(
        status_code=422,
        content=error_response.model_dump(exclude_none=True),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    error_response = ModelResponse(
        success=False,
        message="Đã xảy ra lỗi hệ thống không mong muốn. Vui lòng liên hệ quản trị viên.",
    )
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump(exclude_none=True)
    )