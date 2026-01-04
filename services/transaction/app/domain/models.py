from datetime import date
from enum import Enum
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4


class OperationType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class Transaction(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    asset_id: str
    operation_type: OperationType
    quantity: float
    price: float
    currency: str
    trade_date: date
    idempotency_key: str | None = Field(default=None, index=True, unique=True, nullable=True)
