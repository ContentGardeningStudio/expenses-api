from typing import List, Optional, Tuple
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session
from .models import Category, Expense
from decimal import Decimal
from datetime import datetime


from expenses_api import models

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
    return f"Category {category_id} deleted successfully!"


# The implementation of the Expenses logic


def create_expense(
    db: Session,
    category_id: int,
    amount: Decimal,
    currency: str,
    name: Optional[str] = None,
) -> Expense:
    expense = Expense(
        category_id=category_id, amount=amount, currency=currency.upper(), name=name
    )
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


def update_expense(
    db: Session,
    expense_id: int,
    patch: dict,
    expected_updated_at: Optional[datetime] = None,
) -> Expense:
    exp = db.get(Expense, expense_id)
    if not exp:
        return None
    # optimistic concurrency
    if expected_updated_at is not None:
        if exp.updated_at is None or exp.updated_at.replace(
            tzinfo=None
        ) != expected_updated_at.replace(tzinfo=None):
            raise ValueError("conflict")
    for k, v in patch.items():
        setattr(exp, k, v)
    db.commit()
    db.refresh(exp)
    return exp


def list_expenses(
    db: Session,
    page: int = 1,
    size: int = 50,
    from_dt: Optional[datetime] = None,
    to_dt: Optional[datetime] = None,
    category_id: Optional[int] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
) -> Tuple[List[Expense], int]:
    q = select(Expense)
    if category_id:
        q = q.where(Expense.category_id == category_id)
    if min_amount:
        q = q.where(Expense.amount >= min_amount)
    if max_amount:
        q = q.where(Expense.amount <= max_amount)

    total = db.execute(select(func.count()).select_from(q.subquery())).scalar_one()
    items = db.execute(q).scalars().all()
    return items, total


def summary_by_category(db: Session):
    q = (
        select(
            models.Category.name.label("key"),
            Expense.currency,
            func.sum(Expense.amount).label("total_amount"),
        )
        .join(Expense, Expense.category_id == Category.id)
        .group_by(models.Category.name, Expense.currency)
    )
    return [dict(r._mapping) for r in db.execute(q).all()]


def summary_by_month(db: Session):
    q = text("""
        SELECT
            strftime('%Y-%m', created_at) AS key, 
            currency,
            SUM(amount) AS total_amount
        FROM expenses
        GROUP BY key, currency
        ORDER BY key DESC
    """)
    rows = db.execute(q).all()
    return [dict(r._mapping) for r in rows]
