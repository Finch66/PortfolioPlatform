from datetime import date
from uuid import UUID
from sqlmodel import Session, select

from app.domain.models import Transaction, OperationType
from app.core.events import publish_transaction_created, publish_transaction_deleted

ALLOWED_CURRENCIES = {"USD", "EUR", "GBP"}


class DomainException(Exception):
    pass


class TransactionService:
    def __init__(self, session: Session):
        self.session = session

    def create_transaction(self, transaction: Transaction, idempotency_key: str | None = None) -> Transaction:
        if idempotency_key:
            existing = self.session.exec(
                select(Transaction).where(Transaction.idempotency_key == idempotency_key)
            ).first()
            if existing:
                return existing
            transaction.idempotency_key = idempotency_key

        self._validate_basic_rules(transaction)
        self._validate_sell_quantity(transaction)

        self.session.add(transaction)
        self.session.commit()
        self.session.refresh(transaction)

        publish_transaction_created(
            {
                "id": str(transaction.id),
                "asset_id": transaction.asset_id,
                "operation_type": transaction.operation_type,
                "quantity": transaction.quantity,
                "price": transaction.price,
                "currency": transaction.currency,
                "trade_date": transaction.trade_date.isoformat(),
            }
        )
        return transaction

    def delete_transaction(self, transaction_id: str | UUID) -> None:
        tx_id = transaction_id if isinstance(transaction_id, UUID) else UUID(str(transaction_id))
        tx = self.session.get(Transaction, tx_id)
        if tx is None:
            raise DomainException(f"Transaction {tx_id} not found")
        self.session.delete(tx)
        self.session.commit()
        publish_transaction_deleted(
            {
                "id": str(tx_id),
                "asset_id": tx.asset_id,
                "operation_type": tx.operation_type,
            }
        )

    def _validate_basic_rules(self, transaction: Transaction):
        # Normalize trade_date if it arrives as a string (e.g., from JSON)
        if isinstance(transaction.trade_date, str):
            try:
                transaction.trade_date = date.fromisoformat(transaction.trade_date)
            except ValueError:
                raise DomainException("Invalid trade_date format, expected YYYY-MM-DD")

        if transaction.quantity <= 0:
            raise DomainException("Quantity must be greater than zero")

        if transaction.trade_date > date.today():
            raise DomainException("Trade date cannot be in the future")

        currency = transaction.currency.upper()
        transaction.currency = currency
        if len(currency) != 3:
            raise DomainException("Invalid currency code")
        if currency not in ALLOWED_CURRENCIES:
            raise DomainException(f"Unsupported currency: {currency}")

    def _validate_sell_quantity(self, transaction: Transaction):
        if transaction.operation_type != OperationType.SELL:
            return

        result = self.session.exec(
            select(Transaction)
            .where(Transaction.asset_id == transaction.asset_id)
        ).all()

        total_quantity = 0.0
        for tx in result:
            if tx.operation_type == OperationType.BUY:
                total_quantity += tx.quantity
            else:
                total_quantity -= tx.quantity

        if transaction.quantity > total_quantity:
            raise DomainException(
                f"Cannot sell {transaction.quantity}, only {total_quantity} available"
            )
