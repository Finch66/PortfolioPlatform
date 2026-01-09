from datetime import date
from pydantic import BaseModel, Field
from uuid import UUID


class TransactionCreate(BaseModel):
    asset_id: str = Field(..., description="Asset identifier (e.g., ISIN/ticker)")
    asset_name: str | None = Field(default=None, description="Human readable asset name")
    asset_type: str | None = Field(default=None, description="Asset type (ETF/AZIONE/OBBLIGAZIONE/CRYPTO)")
    operation_type: str = Field(..., description="BUY or SELL")
    quantity: float = Field(..., gt=0, description="Quantity must be > 0")
    price: float = Field(..., gt=0, description="Trade price")
    currency: str = Field(..., min_length=3, max_length=3, description="ISO currency code")
    trade_date: date


class TransactionRead(BaseModel):
    id: UUID
    asset_id: str
    asset_name: str | None = None
    asset_type: str | None = None
    operation_type: str
    quantity: float
    price: float
    currency: str
    trade_date: date


class ImportErrorItem(BaseModel):
    row_number: int
    message: str


class ImportResult(BaseModel):
    inserted: int
    skipped: int
    errors: list[ImportErrorItem]


class HoldingRead(BaseModel):
    asset_id: str
    asset_name: str
    asset_type: str
    currency: str
    quantity: float
    average_cost: float
    last_price: float
    invested: float
    market_value: float
    unrealized_pl: float
    unrealized_pl_pct: float


class AllocationBucket(BaseModel):
    label: str
    market_value: float
    weight: float


class PortfolioAllocation(BaseModel):
    by_asset_type: list[AllocationBucket]
    by_currency: list[AllocationBucket]


class PortfolioMetrics(BaseModel):
    total_assets: int
    total_market_value: float
    total_invested: float
    total_unrealized_pl: float
    total_unrealized_pl_pct: float


class PortfolioSnapshot(BaseModel):
    holdings: list[HoldingRead]
    metrics: PortfolioMetrics
    allocation: PortfolioAllocation
