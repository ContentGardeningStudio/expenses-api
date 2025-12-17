from faker import Faker
from decimal import Decimal
import random

from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import Category, Expense

fake = Faker()

CURRENCIES = ["USD", "EUR"]


def seed_faker():
    db: Session = SessionLocal()

    print("Clearing existing data...")
    db.query(Expense).delete()
    db.query(Category).delete()
    db.commit()

    print("Creating categories...")
    category_names = [fake.word().capitalize() for _ in range(15)]

    categories = [Category(name=name) for name in category_names]

    db.add_all(categories)
    db.commit()

    # Fetch newly created categories with IDs
    db.refresh(categories[0])
    category_ids = [c.id for c in db.query(Category).all()]

    print("Creating fake expenses...")

    expenses = []
    for _ in range(200):
        amount = round(random.uniform(5, 500), 2)

        expenses.append(
            Expense(
                amount=Decimal(str(amount)),
                currency=random.choice(CURRENCIES),
                name=fake.sentence(nb_words=8),
                category_id=random.choice(category_ids),
            )
        )

    db.add_all(expenses)
    db.commit()
    db.close()

    print("Database successfully populated with data")


if __name__ == "__main__":
    seed_faker()
