from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Category, Expense


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
