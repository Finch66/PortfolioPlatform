"""FastAPI application wiring for the Transactions Service."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel

from app.api.transactions import router as transactions_router
from app.core.database import engine
from app.domain.services import DomainException

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("transactions_service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure all SQLModel-defined tables are created before serving requests.
    SQLModel.metadata.create_all(engine)
    yield


# Create the ASGI app with a descriptive title for docs/UIs.
# redirect_slashes=False evita i 307 automatici tra path con/senza trailing slash.
app = FastAPI(title="Transactions Service", redirect_slashes=False, lifespan=lifespan)


@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    logger.warning("Domain error on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=400,
        content={"code": "domain_error", "message": str(exc)},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"code": "internal_error", "message": "Unexpected error"},
    )


# Mount the transactions API routes under their configured prefix.
app.include_router(transactions_router)
