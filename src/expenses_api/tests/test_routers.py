import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from decimal import Decimal
from datetime import datetime

from expenses_api.main import app
from expenses_api.database import Base
from expenses_api.deps import get_session
from expenses_api import models


@pytest.fixture(scope="module")
def engine():
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="module", autouse=True)
def setup_db(engine: Engine):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def override_get_session(engine):
    connection = engine.connect()
    transaction = connection.begin()

    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    def get_test_session():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = get_test_session

    yield session

    app.dependency_overrides = {}
    transaction.rollback()
    connection.close()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def create_test_category(override_get_session: Session):
    # Helper to pre-populate a category
    category = models.Category(name="Test Category")
    override_get_session.add(category)
    override_get_session.commit()
    override_get_session.refresh(category)
    return category


def test_post_category_success(client: TestClient):
    response = client.post("/categories", json={"name": "Travel"})
    assert response.status_code == 201
    assert response.json()["name"] == "Travel"


def test_post_expense_success(client: TestClient, create_test_category: models.Category):
    payload = {
        "category_id": create_test_category.id,
        "amount": 55.50,
        "currency": "usd",
        "name": "New Shirt Purchase"
    }
    response = client.post("/expenses", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["currency"] == "USD"
    assert data["amount"] == 55.50
    assert "id" in data


def test_post_expense_unsupported_currency(client: TestClient, create_test_category: models.Category):
    payload = {
        "category_id": create_test_category.id,
        "amount": 10.00,
        "currency": "GBP",
        "name": "Invalid currency"
    }

    response = client.post("/expenses", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported currency for now"


def test_get_expense_by_id_success(client: TestClient, override_get_session: Session, create_test_category: models.Category):

    expense = models.Expense(
        category_id=create_test_category.id,
        amount=Decimal("100.00"),
        currency="EUR",
        name="Test Item"
    )
    override_get_session.add(expense)
    override_get_session.commit()
    override_get_session.refresh(expense)

    response = client.get(f"/expenses/{expense.id}")
    assert response.status_code == 200
    assert response.json()["amount"] == 100.0


def test_get_list_pagination(client: TestClient, override_get_session: Session, create_test_category: models.Category):
    for i in range(3):
        override_get_session.add(models.Expense(
            category_id=create_test_category.id,
            amount=Decimal(f"10.{i}"),
            currency="USD",
        ))
    override_get_session.commit()

    response = client.get("/expenses?page=1&size=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2
