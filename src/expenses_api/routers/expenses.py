from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from decimal import Decimal

from expenses_api.security import get_current_user
from ..deps import get_session
from ..schemas import ExpenseCreate, ExpenseOut, PaginatedExpenses
from ..crud import create_expense, get_expense, list_expenses, delete_expense
from ..models import Expense
from ..models import User


router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post("", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def post_expense(payload: ExpenseCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):

    if payload.currency.upper() not in {"EUR", "USD"}:
        raise HTTPException(
            status_code=400, detail="Unsupported currency for now")
    return create_expense(db, payload.category_id, Decimal(payload.amount), payload.currency.upper(), payload.name)


@router.get("/{expense_id}", response_model=ExpenseOut)
def get_one(expense_id: int, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    expense = get_expense(db, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.get("", response_model=PaginatedExpenses)
def get_list(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    category_id: Optional[int] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    items, total = list_expenses(
        db=db,
        page=page,
        size=size,
        category_id=category_id,
        min_amount=min_amount,
        max_amount=max_amount,
    )

    return PaginatedExpenses(
        page=page,
        size=size,
        total=total,
        items=items,
    )


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(expense_id: int, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    obj = db.get(Expense, expense_id)

    if obj is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return delete_expense(db, expense_id)
