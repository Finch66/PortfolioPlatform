from datetime import date
from pydantic import BaseModel, Field
from uuid import UUID


class TransactionCreate(BaseModel):
    asset_id: str = Field(..., description="Asset identifier (e.g., ISIN/ticker)")
    operation_type: str = Field(..., description="BUY or SELL")
    quantity: float = Field(..., gt=0, description="Quantity must be > 0")
    price: float = Field(..., gt=0, description="Trade price")
    currency: str = Field(..., min_length=3, max_length=3, description="ISO currency code")
    trade_date: date


class TransactionRead(BaseModel):
    id: UUID
    asset_id: str
    operation_type: str
    quantity: float
    price: float
    currency: str
    trade_date: date
