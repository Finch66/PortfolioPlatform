from uuid import UUID

from fastapi import APIRouter, Depends, Response, Header
from sqlmodel import Session, select

from app.core.errors import NotFoundException
from app.api.schemas import TransactionCreate, TransactionRead
from app.core.database import get_session
from app.domain.models import Transaction
from app.domain.services import TransactionService, DomainException

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=TransactionRead)
@router.post("/", response_model=TransactionRead, include_in_schema=False)
def create_transaction(
    transaction_in: TransactionCreate,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    session: Session = Depends(get_session),
):
    service = TransactionService(session)
    transaction = Transaction(**transaction_in.model_dump())
    return service.create_transaction(transaction, idempotency_key=idempotency_key)


@router.get("", response_model=list[TransactionRead])
@router.get("/", response_model=list[TransactionRead], include_in_schema=False)
def list_transactions(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
):
    stmt = select(Transaction).offset(skip).limit(limit)
    return session.exec(stmt).all()


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(
    transaction_id: UUID,
    session: Session = Depends(get_session),
):
    service = TransactionService(session)
    try:
        service.delete_transaction(str(transaction_id))
    except DomainException as exc:
        raise NotFoundException(str(exc))
    return Response(status_code=204)
