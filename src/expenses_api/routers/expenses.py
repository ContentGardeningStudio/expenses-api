from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal
from ..deps import get_session
from ..schemas import ExpenseCreate, ExpenseOut
from ..repositories import create_expense, get_expense


router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def post_expense(payload: ExpenseCreate, db: Session = Depends(get_session)):

    if payload.currency.upper() not in {"EUR", "USD"}:
        raise HTTPException(
            status_code=400, detail="Unsupported currency for now")
    return create_expense(db, payload.category_id, Decimal(payload.amount), payload.currency.upper(), payload.note)


@router.get("/{expense_id}", response_model=ExpenseOut)
def get_one(expense_id: int, db: Session = Depends(get_session)):
    expense = get_expense(db, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Not found")
    return expense
