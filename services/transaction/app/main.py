"""FastAPI application wiring for the Transactions Service."""

from fastapi import FastAPI
from app.api.transactions import router as transactions_router
from app.core.database import engine
from sqlmodel import SQLModel

# Create the ASGI app with a descriptive title for docs/UIs.
app = FastAPI(title="Transactions Service")

# Mount the transactions API routes under their configured prefix.
app.include_router(transactions_router)


@app.on_event("startup")
def on_startup():
    # Ensure all SQLModel-defined tables are created before serving requests.
    SQLModel.metadata.create_all(engine)
