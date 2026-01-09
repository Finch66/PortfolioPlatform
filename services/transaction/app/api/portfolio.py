from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.api.schemas import (
    PortfolioAllocation,
    PortfolioMetrics,
    PortfolioSnapshot,
    HoldingRead,
    AllocationBucket,
)
from app.core.database import get_session
from app.domain.models import Transaction
from app.domain.portfolio import build_portfolio_snapshot

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("", response_model=PortfolioSnapshot)
@router.get("/", response_model=PortfolioSnapshot, include_in_schema=False)
def get_portfolio(session: Session = Depends(get_session)):
    transactions = session.exec(select(Transaction)).all()
    snapshot = build_portfolio_snapshot(transactions)
    return PortfolioSnapshot(
        holdings=[HoldingRead(**h.__dict__) for h in snapshot.holdings],
        metrics=PortfolioMetrics(**snapshot.metrics.__dict__),
        allocation=PortfolioAllocation(
            by_asset_type=[AllocationBucket(**b.__dict__) for b in snapshot.allocation_by_asset_type],
            by_currency=[AllocationBucket(**b.__dict__) for b in snapshot.allocation_by_currency],
        ),
    )


@router.get("/metrics", response_model=PortfolioMetrics)
def get_portfolio_metrics(session: Session = Depends(get_session)):
    transactions = session.exec(select(Transaction)).all()
    snapshot = build_portfolio_snapshot(transactions)
    return PortfolioMetrics(**snapshot.metrics.__dict__)


@router.get("/allocation", response_model=PortfolioAllocation)
def get_portfolio_allocation(session: Session = Depends(get_session)):
    transactions = session.exec(select(Transaction)).all()
    snapshot = build_portfolio_snapshot(transactions)
    return PortfolioAllocation(
        by_asset_type=[AllocationBucket(**b.__dict__) for b in snapshot.allocation_by_asset_type],
        by_currency=[AllocationBucket(**b.__dict__) for b in snapshot.allocation_by_currency],
    )
