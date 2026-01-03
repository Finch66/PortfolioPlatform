from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.api.schemas import TransactionCreate, TransactionRead
from app.core.database import get_session
from app.domain.models import Transaction
from app.domain.services import TransactionService

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=TransactionRead)
@router.post("/", response_model=TransactionRead, include_in_schema=False)
def create_transaction(
    transaction_in: TransactionCreate,
    session: Session = Depends(get_session),
):
    service = TransactionService(session)
    transaction = Transaction(**transaction_in.model_dump())
    return service.create_transaction(transaction)


@router.get("", response_model=list[TransactionRead])
@router.get("/", response_model=list[TransactionRead], include_in_schema=False)
def list_transactions(
    session: Session = Depends(get_session),
):
    return session.exec(select(Transaction)).all()
