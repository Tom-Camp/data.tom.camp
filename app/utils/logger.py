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
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno  # type: ignore[assignment]

        frame, depth = sys._getframe(6), 6
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore[assignment]
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


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
    logger.remove()

    if json:
        logger.add(
            sys.stdout,
            level=level,
            serialize=True,
            backtrace=False,
            diagnose=False,
        )
    else:
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
            diagnose=True,
        )

    if log_file:
        logger.add(
            log_file,
            level=level,
            rotation="10 MB",
            retention="14 days",
            compression="gz",
            backtrace=True,
            diagnose=False,
            enqueue=True,
        )

    # Forward all stdlib logging records into Loguru
    logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)

    # Silence noisy libraries polluting your logs
    for noisy in (
        "uvicorn.access",
        "sqlalchemy.engine",
        "sqlalchemy.pool",
        "sqlalchemy.dialects",
    ):
        logging.getLogger(noisy).setLevel(logging.WARNING)


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
