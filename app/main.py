from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from loguru import logger

from app.api.v1.device_router import device_routes
from app.utils.config import settings
from app.utils.database import create_db_and_tables
from app.utils.logger import setup_logging
from app.utils.middleware import RequestLoggingMiddleware

setup_logging(
    level=settings.LOG_LEVEL,
    json=settings.LOG_JSON_FORMAT,
    log_file=settings.LOG_NAME,  # e.g. "/var/log/app/api.log"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — creating database tables")
    await create_db_and_tables()
    logger.info("Startup complete")
    yield
    logger.info("Shutting down")


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


app.include_router(device_routes.router, prefix="/api")


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
