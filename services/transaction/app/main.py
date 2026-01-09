"""FastAPI application wiring for the Transactions Service."""

import logging
import os
import sys
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pythonjsonlogger import jsonlogger
from sqlmodel import SQLModel

from app.api.imports import router as imports_router
from app.api.portfolio import router as portfolio_router
from app.api.transactions import router as transactions_router
from app.core.database import engine
from app.core.errors import NotFoundException
from app.domain.services import DomainException

handler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(method)s %(path)s %(status_code)s %(duration_ms)s"
)
handler.setFormatter(formatter)
logger = logging.getLogger("transactions_service")
logger.setLevel(logging.INFO)
logger.handlers = [handler]
logger.propagate = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure all SQLModel-defined tables are created before serving requests.
    SQLModel.metadata.create_all(engine)
    yield


# Create the ASGI app with a descriptive title for docs/UIs.
# redirect_slashes=False evita i 307 automatici tra path con/senza trailing slash.
app = FastAPI(title="Transactions Service", redirect_slashes=False, lifespan=lifespan)

origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
        },
    )
    return response


@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    request_id = getattr(request.state, "request_id", None)
    logger.warning(
        "Domain error",
        extra={"request_id": request_id, "method": request.method, "path": request.url.path},
    )
    return JSONResponse(
        status_code=400,
        content={"code": "domain_error", "message": str(exc)},
    )


@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request: Request, exc: NotFoundException):
    request_id = getattr(request.state, "request_id", None)
    logger.info(
        "Not found",
        extra={"request_id": request_id, "method": request.method, "path": request.url.path},
    )
    return JSONResponse(
        status_code=404,
        content={"code": "not_found", "message": str(exc)},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", None)
    logger.exception(
        "Unhandled error",
        extra={"request_id": request_id, "method": request.method, "path": request.url.path},
    )
    return JSONResponse(
        status_code=500,
        content={"code": "internal_error", "message": "Unexpected error"},
    )


# Mount the transactions API routes under their configured prefix.
app.include_router(transactions_router)
app.include_router(imports_router)
app.include_router(portfolio_router)
