from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.database import get_session
from app.domain.models import Transaction

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", response_model=Transaction)
def create_transaction(
    transaction: Transaction,
    session: Session = Depends(get_session),
):
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


@router.get("/", response_model=list[Transaction])
def list_transactions(
    session: Session = Depends(get_session),
):
    return session.exec(select(Transaction)).all()
