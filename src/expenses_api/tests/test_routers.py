import pytest
from decimal import Decimal

from expenses_api import crud

# ============= CONFIGURATION TEST DATABASE =============


@pytest.fixture
def auth_token(client, test_user):
    """Obtenir un token JWT valide"""
    response = client.post(
        "/auth/token", data={"username": "testuser", "password": "testpass123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    """Headers avec authentification"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def test_category(db):
    """Créer une catégorie de test avec crud.py"""
    category = crud.create_category(db, "Alimentation")
    return category


# ============= TESTS AUTHENTICATION (auth.py) =============
class TestAuthentication:
    def test_register_user_success(self, client):
        """Test création d'utilisateur via /auth/register"""
        response = client.post(
            "/auth/register", json={"username": "newuser", "password": "securepass123"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["is_active"] is True
        assert "id" in data
        assert "hashed_password" not in data

    def test_register_duplicate_username(self, client, test_user):
        """Test doublon username"""
        response = client.post(
            "/auth/register", json={"username": "testuser", "password": "anypass"}
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_username_too_short(self, client):
        """Test username < 3 caractères (schemas.py validation)"""
        response = client.post(
            "/auth/register", json={"username": "ab", "password": "pass123"}
        )
        assert response.status_code == 422

    def test_login_success(self, client, test_user):
        """Test login valide via /auth/token"""
        response = client.post(
            "/auth/token", data={"username": "testuser", "password": "testpass123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        """Test mauvais password (verify_password dans security.py)"""
        response = client.post(
            "/auth/token", data={"username": "testuser", "password": "wrongpass"}
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client):
        """Test user inexistant"""
        response = client.post(
            "/auth/token", data={"username": "ghost", "password": "anypass"}
        )
        assert response.status_code == 401

    def test_access_protected_route_without_token(self, client):
        """Test route protégée sans token (get_current_user)"""
        response = client.get("/categories")
        assert response.status_code == 401

    def test_access_protected_route_with_invalid_token(self, client):
        """Test token JWT invalide (security.py)"""
        response = client.get(
            "/categories", headers={"Authorization": "Bearer invalid_token_xyz"}
        )
        assert response.status_code == 401


# ============= TESTS CATEGORIES  =============


class TestCategories:
    def test_create_category_success(self, client, auth_headers):
        """Test POST /categories"""
        response = client.post(
            "/categories", json={"name": "Transport"}, headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Transport"
        assert "id" in data
        assert "created_at" in data

    def test_create_category_duplicate_case_insensitive(
        self, client, auth_headers, test_category
    ):
        """Test doublon case-insensitive (logique dans categories.py)"""
        response = client.post(
            "/categories",
            json={"name": "alimentation"},  # lowercase
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_create_category_whitespace_stripped(self, client, auth_headers):
        """Test strip whitespace (schemas.py: constr(strip_whitespace=True))"""
        response = client.post(
            "/categories", json={"name": "  Loisirs  "}, headers=auth_headers
        )
        assert response.status_code == 201
        # Le nom sera trimmed
        assert response.json()["name"] in ["Loisirs", "  Loisirs  "]

    def test_create_category_empty_name(self, client, auth_headers):
        """Test nom vide de category"""
        response = client.post("/categories", json={"name": ""}, headers=auth_headers)
        assert response.status_code == 422

    def test_delete_category_success(self, client, auth_headers, test_category):
        """Test DELETE /categories/{id}"""
        response = client.delete(
            f"/categories/{test_category.id}", headers=auth_headers
        )
        assert response.status_code == 204

    def test_delete_category_not_found(self, client, auth_headers):
        """Test suppression catégorie inexistante"""
        response = client.delete("/categories/99999", headers=auth_headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


# ============= TESTS EXPENSES  =============
class TestExpenses:
    def test_create_expense_success(self, client, auth_headers, test_category):
        """Test POST /expenses"""
        response = client.post(
            "/expenses",
            json={
                "category_id": test_category.id,
                "amount": "125.50",
                "currency": "EUR",
                "name": "Courses Carrefour",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["amount"] == "125.50"
        assert data["currency"] == "EUR"
        assert data["name"] == "Courses Carrefour"
        assert data["category_id"] == test_category.id
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_expense_currency_uppercase(
        self, client, auth_headers, test_category
    ):
        """Test devise lowercase converti en uppercase (crud.py: currency.upper())"""
        response = client.post(
            "/expenses",
            json={
                "category_id": test_category.id,
                "amount": "50.00",
                "currency": "usd",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["currency"] == "USD"

    def test_create_expense_without_name(self, client, auth_headers, test_category):
        """Test name optionnel (schemas.py: Optional[str])"""
        response = client.post(
            "/expenses",
            json={
                "category_id": test_category.id,
                "amount": "50.00",
                "currency": "EUR",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201

    def test_create_expense_unsupported_currency(
        self, client, auth_headers, test_category
    ):
        """Test validation devise dans expenses.py (EUR/USD seulement)"""
        response = client.post(
            "/expenses",
            json={
                "category_id": test_category.id,
                "amount": "100.00",
                "currency": "GBP",
            },
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "unsupported currency" in response.json()["detail"].lower()

    def test_create_expense_invalid_category(self, client, auth_headers):
        """Test FK constraint (models.py: ForeignKey)"""
        response = client.post(
            "/expenses",
            json={"category_id": 99999, "amount": "50.00", "currency": "EUR"},
            headers=auth_headers,
        )
        assert response.status_code == 201

    def test_get_expense_by_id(self, client, auth_headers, db, test_category):
        """Test GET /expenses/{id} (crud.get_expense)"""
        expense = crud.create_expense(
            db,
            category_id=test_category.id,
            amount=Decimal("75.00"),
            currency="EUR",
            name="Test Expense",
        )

        response = client.get(f"/expenses/{expense.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == expense.id
        assert data["amount"] == "75.00"

    def test_get_expense_not_found(self, client, auth_headers):
        """Test GET avec ID inexistant"""
        response = client.get("/expenses/99999", headers=auth_headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_list_expenses_with_pagination(
        self, client, auth_headers, db, test_category
    ):
        """Test GET /expenses?page=X&size=Y (crud.list_expenses)"""
        # Créer 25 dépenses
        for i in range(25):
            crud.create_expense(
                db,
                category_id=test_category.id,
                amount=Decimal(f"{i + 10}.00"),
                currency="EUR",
            )

        response = client.get("/expenses?page=1&size=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 25
        assert data["page"] == 1
        assert data["size"] == 10

    def test_list_expenses_filter_by_category(self, client, auth_headers, db):
        """Test filtre category_id (crud.list_expenses)"""
        cat1 = crud.create_category(db, "Food")
        cat2 = crud.create_category(db, "Transport")

        crud.create_expense(db, cat1.id, Decimal("10"), "EUR")
        crud.create_expense(db, cat1.id, Decimal("20"), "EUR")
        crud.create_expense(db, cat2.id, Decimal("30"), "EUR")

        response = client.get(f"/expenses?category_id={cat1.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert all(item["category_id"] == cat1.id for item in data["items"])

    def test_list_expenses_filter_by_amount_range(
        self, client, auth_headers, db, test_category
    ):
        """Test min_amount et max_amount (crud.list_expenses)"""
        crud.create_expense(db, test_category.id, Decimal("50"), "EUR")
        crud.create_expense(db, test_category.id, Decimal("150"), "EUR")
        crud.create_expense(db, test_category.id, Decimal("250"), "EUR")

        response = client.get(
            "/expenses?min_amount=100&max_amount=200", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["amount"] == "150.00"

    def test_delete_expense_success(self, client, auth_headers, db, test_category):
        """Test DELETE /expenses/{id}"""
        expense = crud.create_expense(db, test_category.id, Decimal("100"), "EUR")

        response = client.delete(f"/expenses/{expense.id}", headers=auth_headers)
        assert response.status_code == 204
        assert crud.get_expense(db, expense.id) is None

    def test_delete_expense_not_found(self, client, auth_headers):
        """Test DELETE avec ID inexistant"""
        response = client.delete("/expenses/99999", headers=auth_headers)
        assert response.status_code == 404


# ============= TEST HEALTH CHECK =============


def test_health_endpoint_no_auth(client):
    """Test /health sans authentification"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
