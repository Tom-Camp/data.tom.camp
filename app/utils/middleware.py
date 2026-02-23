import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.logger import log_context


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Attaches a unique request_id to every log record produced during the
    request lifetime and emits a structured access log on completion.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = str(uuid.uuid4())
        start = time.perf_counter()

        with log_context(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        ):
            logger.debug("Request started")
            try:
                response = await call_next(request)
            except Exception:
                logger.exception("Unhandled exception during request")
                raise

            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.info(
                "Request completed | status={status} elapsed={elapsed:.1f}ms",
                status=response.status_code,
                elapsed=elapsed_ms,
            )

            response.headers["X-Request-ID"] = request_id
            return response
