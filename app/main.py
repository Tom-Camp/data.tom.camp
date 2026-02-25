from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from loguru import logger
from sqlalchemy.exc import IntegrityError

from app.api.v1.api_key_routes import api_key_routes
from app.api.v1.data_routes import data_routes
from app.api.v1.device_routes import device_routes
from app.utils.config import settings
from app.utils.database import create_db_and_tables, dispose_engine
from app.utils.logger import setup_logging
from app.utils.middleware import RequestLoggingMiddleware

setup_logging(
    level=settings.LOG_LEVEL,
    json=settings.LOG_JSON_FORMAT,
    log_file=settings.LOG_NAME,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — creating database tables")
    await create_db_and_tables()
    logger.info("Startup complete")
    yield
    logger.info("Shutting down")
    await dispose_engine()
    logger.info("Shutdown complete — engine disposed")


app = FastAPI(
    lifespan=lifespan,
    title=settings.APP_NAME,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.bind(path=request.url.path, method=request.method).info("request_start")
    response = await call_next(request)
    logger.bind(
        path=request.url.path,
        method=request.method,
        status_code=response.status_code,
    ).info("request_end")
    return response


app.include_router(api_key_routes, prefix="/api")
app.include_router(data_routes, prefix="/api")
app.include_router(device_routes, prefix="/api")


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.exception_handler(RequestValidationError)
async def custom_422_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Invalid request data",
        },
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    # You can inspect `exc.orig` / `str(exc.orig)` to route to different messages
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Integrity error: constraint violated"},
    )
