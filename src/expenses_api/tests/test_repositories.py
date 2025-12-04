import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from datetime import datetime, timedelta
from decimal import Decimal
import time

from expenses_api import models
from expenses_api import repositories
from expenses_api.database import Base

# --- PYTEST FIXTURES FOR DB SETUP  ---


@pytest.fixture(scope="module")
def engine():
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="module", autouse=True)
def setup_db(engine: Engine):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(engine: Engine):
    connection = engine.connect()
    transaction = connection.begin()

    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def test_category(db_session: Session) -> models.Category:
    return repositories.create_category(db_session, name="Groceries")


# --- TESTS FOR CATEGORY LOGIC  ---

def test_create_category(db_session: Session):
    name = "Rent"
    category = repositories.create_category(db_session, name=name)

    assert category.id is not None
    assert category.name == name
    assert isinstance(category.created_at, datetime)


def test_list_categories_ordered(db_session: Session):
    repositories.create_category(db_session, name="Categorie_A")
    repositories.create_category(db_session, name="Categorie_B")

    categories = repositories.list_categories(db_session)

    assert len(categories) == 2
    assert categories[0].name == "Categorie_A"
    assert categories[1].name == "Categorie_B"


def test_delete_category_success(db_session: Session):
    category = repositories.create_category(db_session, name="ToDelete")
    category_id = category.id

    repositories.delete_category(db_session, category_id)

    deleted_category = db_session.get(models.Category, category_id)
    assert deleted_category is None


# --- TESTS FOR EXPENSE CRUD LOGIC ---
def test_create_expense_success(db_session: Session, test_category: models.Category):
    amount = Decimal("100.50")
    currency = "eur"
    name = "Dinner out"

    expense = repositories.create_expense(
        db_session,
        category_id=test_category.id,
        amount=amount,
        currency=currency,
        name=name
    )

    assert expense.id is not None
    assert expense.amount == amount
    assert expense.currency == "EUR"
    assert expense.name == name


def test_get_expense_not_found(db_session: Session):
    expense = repositories.get_expense(db_session, expense_id=999)
    assert expense is None


def test_update_expense_success(db_session: Session, test_category: models.Category):
    expense = repositories.create_expense(
        db_session, category_id=test_category.id, amount=Decimal("10.00"),
        currency="USD"
    )
    db_session.refresh(expense)
    original_updated_at = expense.updated_at

    time.sleep(1.1)

    patch = {"amount": Decimal("15.00"), "name": "Updated Item"}
    updated_expense = repositories.update_expense(
        db_session,
        expense.id,
        patch,
        expected_updated_at=original_updated_at
    )

    assert updated_expense.amount == Decimal("15.00")
    assert updated_expense.name == "Updated Item"
    assert updated_expense.updated_at > original_updated_at


def test_update_expense_optimistic_lock_failure(db_session: Session, test_category: models.Category):
    expense = repositories.create_expense(
        db_session, category_id=test_category.id, amount=Decimal("10.00"),
        currency="USD"
    )

    wrong_updated_at = expense.updated_at + timedelta(seconds=1)

    with pytest.raises(ValueError, match="conflict"):
        repositories.update_expense(
            db_session,
            expense.id,
            {"amount": Decimal("20.00")},
            expected_updated_at=wrong_updated_at
        )

# --- TESTS FOR QUERY & SUMMARY LOGIC ---


def test_list_expenses_with_filters(db_session: Session, test_category: models.Category):
    cat_id = test_category.id

    # Insert test data
    repositories.create_expense(db_session, cat_id, Decimal("10.00"), "USD")
    repositories.create_expense(db_session, cat_id, Decimal("50.00"), "USD")
    repositories.create_expense(db_session, cat_id, Decimal("100.00"), "EUR")

    # Test 1: No filters (should get all 3)
    items, total = repositories.list_expenses(db_session)
    assert total == 3
    assert len(items) == 3

    # Test 2: Min amount filter (amount >= 50.00)
    items, total = repositories.list_expenses(
        db_session, min_amount=Decimal("50.00"))
    assert total == 2
    assert len(items) == 2
    assert all(item.amount >= Decimal("50.00") for item in items)

    # Test 3: Category filter
    items, total = repositories.list_expenses(
        db_session, category_id=cat_id + 1)
    assert total == 0


def test_summary_by_category(db_session: Session, test_category: models.Category):
    cat_id = test_category.id
    repositories.create_category(db_session, name="Transport")
    transport_cat = repositories.list_categories(db_session)[1]

    repositories.create_expense(db_session, cat_id, Decimal("10.00"), "USD")
    repositories.create_expense(db_session, cat_id, Decimal("20.00"), "USD")
    repositories.create_expense(db_session, cat_id, Decimal("50.00"), "EUR")
    repositories.create_expense(
        db_session, transport_cat.id, Decimal("100.00"), "USD")

    summary = repositories.summary_by_category(db_session)

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
