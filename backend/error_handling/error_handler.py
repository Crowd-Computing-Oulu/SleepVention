from functools import wraps
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import logging

# ✅ Enable logging for debugging unexpected errors
logging.basicConfig(level=logging.ERROR)


def exception_handler(func):
    """
    A universal exception handler decorator for FastAPI routes.
    - Catches `ValidationError` (422 errors).
    - Catches `HTTPException` and re-raises it.
    - Catches all other unexpected errors and returns a `400 Bad Request`.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)

        except ValidationError as e:
            logging.error(f"Validation error: {e}")
            return JSONResponse(status_code=422, content={"detail": "Invalid request format"})

        except HTTPException as http_exc:
            return JSONResponse(status_code=http_exc.status_code, content={"detail": http_exc.detail})

        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

    return wrapper
