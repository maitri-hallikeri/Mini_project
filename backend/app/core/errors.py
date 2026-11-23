"""
Centralised error handling and consistent JSON error responses.

Owner: Member 3 (backend core).

Every error returned by the API uses the envelope::

    {"detail": "<human-readable message>", "code": "<machine-readable code>"}

Usage::

    from app.core.errors import AppError, not_found, bad_request
    raise not_found("Incident", incident_id)
"""

from __future__ import annotations

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

# ------------------------------------------------------------------ #
# Error envelope helpers
# ------------------------------------------------------------------ #


class AppError(HTTPException):
    """
    Base application error that always produces the standard JSON envelope.

    Args:
        status_code: HTTP status code.
        detail: Human-readable explanation shown to callers.
        code: Machine-readable error code for programmatic handling.
    """

    def __init__(self, status_code: int, detail: str, code: str) -> None:
        super().__init__(status_code=status_code, detail=detail)
        self.code = code

    def to_dict(self) -> dict[str, str]:
        """Return the JSON envelope dict."""
        return {"detail": self.detail, "code": self.code}


# ------------------------------------------------------------------ #
# Named constructors for common error cases
# ------------------------------------------------------------------ #


def not_found(entity: str, identifier: object) -> AppError:
    """Return a 404 AppError for a missing entity."""
    return AppError(
        status_code=404,
        detail=f"{entity} '{identifier}' not found.",
        code="NOT_FOUND",
    )


def bad_request(detail: str) -> AppError:
    """Return a 400 AppError."""
    return AppError(status_code=400, detail=detail, code="BAD_REQUEST")


def not_implemented_error(owner: str, description: str) -> AppError:
    """Return a 501 AppError for unimplemented stub endpoints."""
    return AppError(
        status_code=501,
        detail=f"TODO({owner}): {description}",
        code="NOT_IMPLEMENTED",
    )


# ------------------------------------------------------------------ #
# FastAPI exception handlers — register in main.py
# ------------------------------------------------------------------ #


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """
    Convert an ``AppError`` into the standard JSON envelope response.

    Register with::

        app.add_exception_handler(AppError, app_error_handler)
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Wrap plain ``HTTPException`` instances in the standard envelope so that
    FastAPI's own 404/405/422 responses also use our format.
    """
    code = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_SERVER_ERROR",
        501: "NOT_IMPLEMENTED",
    }.get(exc.status_code, "ERROR")

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": code},
    )
