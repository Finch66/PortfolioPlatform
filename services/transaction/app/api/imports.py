import csv
import io
from datetime import date

from fastapi import APIRouter, Depends, File, UploadFile
from sqlmodel import Session

from app.api.schemas import ImportResult, ImportErrorItem
from app.core.database import get_session
from app.domain.models import Transaction
from app.domain.services import TransactionService, DomainException

router = APIRouter(prefix="/imports", tags=["imports"])

REQUIRED_COLUMNS = {
    "asset_id",
    "operation_type",
    "quantity",
    "price",
    "currency",
    "trade_date",
}


@router.post("/transactions", response_model=ImportResult)
async def import_transactions_csv(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    content = await file.read()
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    if not reader.fieldnames:
        return ImportResult(inserted=0, skipped=0, errors=[ImportErrorItem(row_number=1, message="Missing header")])

    missing = REQUIRED_COLUMNS.difference(set(reader.fieldnames))
    if missing:
        message = f"Missing columns: {', '.join(sorted(missing))}"
        return ImportResult(inserted=0, skipped=0, errors=[ImportErrorItem(row_number=1, message=message)])

    service = TransactionService(session)
    inserted = 0
    skipped = 0
    errors: list[ImportErrorItem] = []

    for row_number, row in enumerate(reader, start=2):
        try:
            transaction = _row_to_transaction(row)
            idempotency_key = row.get("idempotency_key") or None
            service.create_transaction(transaction, idempotency_key=idempotency_key)
            inserted += 1
        except (ValueError, DomainException) as exc:
            errors.append(ImportErrorItem(row_number=row_number, message=str(exc)))
            skipped += 1

    return ImportResult(inserted=inserted, skipped=skipped, errors=errors)


def _row_to_transaction(row: dict) -> Transaction:
    asset_id = _required(row, "asset_id")
    operation_type = _required(row, "operation_type").upper()
    quantity = _parse_float(_required(row, "quantity"))
    price = _parse_float(_required(row, "price"))
    currency = _required(row, "currency").upper()
    trade_date = _parse_date(_required(row, "trade_date"))

    asset_name = row.get("asset_name") or None
    asset_type = row.get("asset_type") or None

    return Transaction(
        asset_id=asset_id,
        asset_name=asset_name,
        asset_type=asset_type,
        operation_type=operation_type,
        quantity=quantity,
        price=price,
        currency=currency,
        trade_date=trade_date,
    )


def _required(row: dict, key: str) -> str:
    value = row.get(key)
    if value is None or str(value).strip() == "":
        raise ValueError(f"Missing value for {key}")
    return str(value).strip()


def _parse_float(value: str) -> float:
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"Invalid number: {value}") from exc


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Invalid date: {value}") from exc
