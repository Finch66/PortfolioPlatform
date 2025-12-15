from fastapi import FastAPI
from app.api.transactions import router as transactions_router
from app.core.database import engine
from sqlmodel import SQLModel

app = FastAPI(title="Transactions Service")

app.include_router(transactions_router)


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
