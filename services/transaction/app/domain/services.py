from datetime import date
from sqlmodel import Session, select

from app.domain.models import Transaction, OperationType


class DomainException(Exception):
    pass


class TransactionService:
    def __init__(self, session: Session):
        self.session = session

    def create_transaction(self, transaction: Transaction) -> Transaction:
        self._validate_basic_rules(transaction)
        self._validate_sell_quantity(transaction)

        self.session.add(transaction)
        self.session.commit()
        self.session.refresh(transaction)
        return transaction

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

        if len(transaction.currency) != 3:
            raise DomainException("Invalid currency code")

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
