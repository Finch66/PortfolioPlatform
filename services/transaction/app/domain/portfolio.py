from collections import defaultdict
from dataclasses import dataclass

from app.domain.models import OperationType, Transaction


@dataclass
class Holding:
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


@dataclass
class AllocationBucket:
    label: str
    market_value: float
    weight: float


@dataclass
class PortfolioMetrics:
    total_assets: int
    total_market_value: float
    total_invested: float
    total_unrealized_pl: float
    total_unrealized_pl_pct: float


@dataclass
class PortfolioSnapshot:
    holdings: list[Holding]
    metrics: PortfolioMetrics
    allocation_by_asset_type: list[AllocationBucket]
    allocation_by_currency: list[AllocationBucket]


def build_portfolio_snapshot(transactions: list[Transaction]) -> PortfolioSnapshot:
    per_asset: dict[tuple[str, str], dict] = {}
    transactions_sorted = sorted(transactions, key=lambda tx: tx.trade_date)

    for tx in transactions_sorted:
        key = (tx.asset_id, tx.currency)
        entry = per_asset.setdefault(
            key,
            {
                "asset_id": tx.asset_id,
                "asset_name": tx.asset_name or "Unknown Asset",
                "asset_type": tx.asset_type or "UNKNOWN",
                "currency": tx.currency,
                "quantity": 0.0,
                "invested": 0.0,
                "last_price": 0.0,
            },
        )
        if tx.asset_name:
            entry["asset_name"] = tx.asset_name
        if tx.asset_type:
            entry["asset_type"] = tx.asset_type

        multiplier = 1.0 if tx.operation_type == OperationType.BUY else -1.0
        entry["quantity"] += multiplier * tx.quantity
        entry["invested"] += multiplier * tx.quantity * tx.price
        entry["last_price"] = tx.price

    holdings: list[Holding] = []
    for entry in per_asset.values():
        quantity = entry["quantity"]
        if quantity <= 0:
            continue
        invested = entry["invested"]
        last_price = entry["last_price"]
        market_value = quantity * last_price
        unrealized_pl = market_value - invested
        unrealized_pl_pct = (unrealized_pl / invested) if invested else 0.0
        average_cost = (invested / quantity) if quantity else 0.0
        holdings.append(
            Holding(
                asset_id=entry["asset_id"],
                asset_name=entry["asset_name"],
                asset_type=entry["asset_type"],
                currency=entry["currency"],
                quantity=round(quantity, 6),
                average_cost=round(average_cost, 4),
                last_price=round(last_price, 4),
                invested=round(invested, 2),
                market_value=round(market_value, 2),
                unrealized_pl=round(unrealized_pl, 2),
                unrealized_pl_pct=round(unrealized_pl_pct, 6),
            )
        )

    holdings.sort(key=lambda h: h.market_value, reverse=True)

    total_market_value = sum(h.market_value for h in holdings)
    total_invested = sum(h.invested for h in holdings)
    total_unrealized_pl = total_market_value - total_invested
    total_unrealized_pl_pct = (total_unrealized_pl / total_invested) if total_invested else 0.0

    allocation_by_asset_type = _build_allocation(
        holdings, key_fn=lambda h: h.asset_type, total_market_value=total_market_value
    )
    allocation_by_currency = _build_allocation(
        holdings, key_fn=lambda h: h.currency, total_market_value=total_market_value
    )

    metrics = PortfolioMetrics(
        total_assets=len(holdings),
        total_market_value=round(total_market_value, 2),
        total_invested=round(total_invested, 2),
        total_unrealized_pl=round(total_unrealized_pl, 2),
        total_unrealized_pl_pct=round(total_unrealized_pl_pct, 6),
    )

    return PortfolioSnapshot(
        holdings=holdings,
        metrics=metrics,
        allocation_by_asset_type=allocation_by_asset_type,
        allocation_by_currency=allocation_by_currency,
    )


def _build_allocation(holdings: list[Holding], key_fn, total_market_value: float) -> list[AllocationBucket]:
    buckets: dict[str, float] = defaultdict(float)
    for holding in holdings:
        buckets[key_fn(holding)] += holding.market_value

    allocation: list[AllocationBucket] = []
    for label, market_value in buckets.items():
        weight = (market_value / total_market_value) if total_market_value else 0.0
        allocation.append(
            AllocationBucket(
                label=label,
                market_value=round(market_value, 2),
                weight=round(weight, 6),
            )
        )

    allocation.sort(key=lambda b: b.market_value, reverse=True)
    return allocation
