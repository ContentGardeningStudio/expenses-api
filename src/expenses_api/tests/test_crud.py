import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from datetime import datetime, timedelta
from decimal import Decimal
import time

from expenses_api import models
from expenses_api import crud
from expenses_api.database import Base

# --- PYTEST FIXTURES FOR DB SETUP  ---


@pytest.fixture
def test_category(db: Session) -> models.Category:
    return crud.create_category(db, name="Groceries")


# --- TESTS FOR CATEGORY LOGIC  ---

def test_create_category(db):
    name = "Rent"
    category = crud.create_category(db, name=name)

    assert category.id is not None
    assert category.name == name
    assert isinstance(category.created_at, datetime)


def test_list_categories_ordered(db):
    crud.create_category(db, name="Categorie_A")
    crud.create_category(db, name="Categorie_B")

    categories = crud.list_categories(db)

    assert len(categories) == 2
    assert categories[0].name == "Categorie_A"
    assert categories[1].name == "Categorie_B"


def test_delete_category_success(db: Session):
    category = crud.create_category(db, name="ToDelete")
    category_id = category.id

    crud.delete_category(db, category_id)

    deleted_category = db.get(models.Category, category_id)
    assert deleted_category is None


# --- TESTS FOR EXPENSE CRUD LOGIC ---
def test_create_expense_success(db: Session, test_category: models.Category):
    amount = Decimal("100.50")
    currency = "eur"
    name = "Dinner out"

    expense = crud.create_expense(
        db,
        category_id=test_category.id,
        amount=amount,
        currency=currency,
        name=name
    )

    assert expense.id is not None
    assert expense.amount == amount
    assert expense.currency == "EUR"
    assert expense.name == name


def test_get_expense_not_found(db: Session):
    expense = crud.get_expense(db, expense_id=999)
    assert expense is None


def test_update_expense_success(db: Session, test_category: models.Category):
    expense = crud.create_expense(
        db, category_id=test_category.id, amount=Decimal("10.00"),
        currency="USD"
    )
    db.refresh(expense)
    original_updated_at = expense.updated_at

    time.sleep(1.1)

    patch = {"amount": Decimal("15.00"), "name": "Updated Item"}
    updated_expense = crud.update_expense(
        db,
        expense.id,
        patch,
        expected_updated_at=original_updated_at
    )

    assert updated_expense.amount == Decimal("15.00")
    assert updated_expense.name == "Updated Item"
    assert updated_expense.updated_at > original_updated_at


def test_update_expense_optimistic_lock_failure(db: Session, test_category: models.Category):
    expense = crud.create_expense(
        db, category_id=test_category.id, amount=Decimal("10.00"),
        currency="USD"
    )

    wrong_updated_at = expense.updated_at + timedelta(seconds=1)

    with pytest.raises(ValueError, match="conflict"):
        crud.update_expense(
            db,
            expense.id,
            {"amount": Decimal("20.00")},
            expected_updated_at=wrong_updated_at
        )

# --- TESTS FOR QUERY & SUMMARY LOGIC ---


def test_list_expenses_with_filters(db: Session, test_category: models.Category):
    cat_id = test_category.id

    # Insert test data
    crud.create_expense(db, cat_id, Decimal("10.00"), "USD")
    crud.create_expense(db, cat_id, Decimal("50.00"), "USD")
    crud.create_expense(db, cat_id, Decimal("100.00"), "EUR")

    # Test 1: No filters (should get all 3)
    items, total = crud.list_expenses(db)
    assert total == 3
    assert len(items) == 3

    # Test 2: Min amount filter (amount >= 50.00)
    items, total = crud.list_expenses(
        db, min_amount=Decimal("50.00"))
    assert total == 2
    assert len(items) == 2
    assert all(item.amount >= Decimal("50.00") for item in items)

    # Test 3: Category filter
    items, total = crud.list_expenses(
        db, category_id=cat_id + 1)
    assert total == 0


def test_summary_by_category(db: Session, test_category: models.Category):
    cat_id = test_category.id
    crud.create_category(db, name="Transport")
    transport_cat = crud.list_categories(db)[1]

    crud.create_expense(db, cat_id, Decimal("10.00"), "USD")
    crud.create_expense(db, cat_id, Decimal("20.00"), "USD")
    crud.create_expense(db, cat_id, Decimal("50.00"), "EUR")
    crud.create_expense(
        db, transport_cat.id, Decimal("100.00"), "USD")

    summary = crud.summary_by_category(db)

    expected = [
        {'key': 'Groceries', 'currency': 'EUR',
            'total_amount': Decimal('50.00')},
        {'key': 'Groceries', 'currency': 'USD',
            'total_amount': Decimal('30.00')},
        {'key': 'Transport', 'currency': 'USD',
            'total_amount': Decimal('100.00')}
    ]

    def sort_key(d):
        return (d['key'], d['currency'])

    assert sorted(summary, key=sort_key) == sorted(expected, key=sort_key)
