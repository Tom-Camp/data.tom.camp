import logging
import sys
from collections.abc import Iterator
from contextlib import contextmanager

from loguru import logger

# ---------------------------------------------------------------------------
# Intercept stdlib logging → Loguru
# ---------------------------------------------------------------------------
# Libraries like SQLAlchemy, uvicorn, and FastAPI use the stdlib `logging`
# module. This handler forwards all of those records into Loguru so you get
# a single, unified log stream.


class _InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Map stdlib level to Loguru level name
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno  # type: ignore[assignment]

        # Walk the call stack to find the real caller (skip logging internals)
        frame, depth = sys._getframe(6), 6
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore[assignment]
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


# ---------------------------------------------------------------------------
# Public setup function — call once at startup
# ---------------------------------------------------------------------------


def setup_logging(
    *,
    level: str = "INFO",
    json: bool = False,
    log_file: str | None = None,
) -> None:
    """
    Configure Loguru as the single logging backend for the entire application.

    :param level:    Minimum log level ("DEBUG", "INFO", "WARNING", …).
    :param json:     Emit structured JSON lines instead of pretty text (set True in prod).
    :param log_file: Optional path for a rotating file sink alongside stdout.
    """
    # Remove the default Loguru sink before adding our own
    logger.remove()

    if json:
        # Structured JSON — ideal for log aggregators (Datadog, Loki, etc.)
        logger.add(
            sys.stdout,
            level=level,
            serialize=True,  # Loguru's built-in JSON serialisation
            backtrace=False,  # Keep traces out of structured logs
            diagnose=False,  # Avoid leaking local variable values
        )
    else:
        # Human-readable coloured output for local development
        fmt = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        logger.add(
            sys.stdout,
            format=fmt,
            level=level,
            colorize=True,
            backtrace=True,
            diagnose=True,  # Print local variable values in tracebacks
        )

    # Optional rotating file sink (always plain text for easy grepping)
    if log_file:
        logger.add(
            log_file,
            level=level,
            rotation="10 MB",
            retention="14 days",
            compression="gz",
            backtrace=True,
            diagnose=False,  # Never write local vars to disk (PII risk)
            enqueue=True,  # Non-blocking writes via a background thread
        )

    # Forward all stdlib logging records into Loguru
    logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)

    # Silence noisy libraries you don't want polluting your logs
    for noisy in (
        "uvicorn.access",
        "sqlalchemy.engine",
        "sqlalchemy.pool",
        "sqlalchemy.dialects",
    ):
        logging.getLogger(noisy).setLevel(logging.WARNING)


# ---------------------------------------------------------------------------
# Request-scoped context helper
# ---------------------------------------------------------------------------


@contextmanager
def log_context(**kwargs: object) -> Iterator[None]:
    """
    Bind arbitrary key/value pairs to every log record inside this block.

    Usage:
        with log_context(request_id=req_id, user_id=user.id):
            logger.info("Handling request")
    """
    with logger.contextualize(**kwargs):
        yield
