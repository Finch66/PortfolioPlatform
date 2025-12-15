from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.database import get_session
from app.domain.models import Transaction
from app.domain.services import TransactionService, DomainException

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", response_model=Transaction)
def create_transaction(
    transaction: Transaction,
    session: Session = Depends(get_session),
):
    service = TransactionService(session)

    try:
        return service.create_transaction(transaction)
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[Transaction])
def list_transactions(
    session: Session = Depends(get_session),
):
    return session.exec(select(Transaction)).all()
