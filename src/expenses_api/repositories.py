from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Category, Expense
from decimal import Decimal
from datetime import datetime

# The implementation of the category logic


def create_category(db: Session, name: str) -> Category:
    category = Category(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def list_categories(db: Session) -> List[Category]:
    return db.execute(select(Category).order_by(Category.name)).scalars().all()


def delete_category(db: Session, category_id: int) -> None:
    category = db.get(Category, category_id)
    if not category:
        return None
    db.delete(category)
    db.commit()
    return None

# The implementation of the Expenses logic


def create_expense(db: Session, category_id: int, amount: Decimal, currency: str, occurred_at: datetime, note: Optional[str] = None) -> Expense:
    expense = Expense(category_id=category_id, amount=amount,
                      currency=currency.upper(), note=note)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def get_expense(db: Session, expense_id: int) -> Optional[Expense]:
    return db.get(Expense, expense_id)


def delete_expense(db: Session, expense_id: int) -> None:
    expense = db.get(Expense, expense_id)
    if not expense:
        return None
    db.delete(expense)
    db.commit()
    return None
