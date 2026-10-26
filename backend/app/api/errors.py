from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.services.errors import (
    DomainError,
    DuplicateEmployee,
    EmployeeNotFound,
    EmployeeTerminated,
)

STATUS_BY_ERROR: dict[type[DomainError], int] = {
    EmployeeNotFound: status.HTTP_404_NOT_FOUND,
    DuplicateEmployee: status.HTTP_409_CONFLICT,
    EmployeeTerminated: status.HTTP_409_CONFLICT,
}


def error_body(code: str, message: str, fields: dict[str, str]) -> dict[str, object]:
    return {"error": {"code": code, "message": message, "fields": fields}}


async def handle_domain_error(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, DomainError)
    status_code = STATUS_BY_ERROR.get(type(exc), status.HTTP_422_UNPROCESSABLE_CONTENT)
    return JSONResponse(error_body(exc.code, exc.message, exc.fields), status_code=status_code)


async def handle_request_validation(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    fields = {
        ".".join(str(part) for part in error["loc"][1:]) or "request": error["msg"]
        for error in exc.errors()
    }
    return JSONResponse(
        error_body("validation_error", "Some fields are invalid", fields),
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, handle_domain_error)
    app.add_exception_handler(RequestValidationError, handle_request_validation)
