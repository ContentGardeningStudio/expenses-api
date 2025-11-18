from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Category, Expense


def create_category(db: Session, name: str) -> Category:
    category = Category(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def list_categories(db: Session) -> List[Category]:
    return db.execute(select(Category).order_by(Category.name)).scalars().all()
