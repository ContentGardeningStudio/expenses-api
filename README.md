# 📘 Expense Tracker API

A simple and clean **FastAPI** backend for managing personal expenses with user authentication, category management, and comprehensive expense tracking.

---

## ✨ Features

- 🔐 **JWT Authentication** - Secure user registration and login with Argon2 password hashing
- 👤 **User Management** - User registration, authentication
- 📂 **Category Management** - Create, list, and delete expense categories
- 💰 **Expense Tracking** - Full CRUD operations for expenses with:
  - Multiple currency support (EUR, USD)
  - Pagination and filtering
  - Amount range queries
  - Category-based filtering
- 📊 **Reporting** - Summary views by category and month
- 🔄 **Optimistic Locking** - Prevents concurrent update conflicts
- ✅ **Comprehensive Testing** - Full test coverage with pytest
- 🗄️ **SQLite Database** - Easy setup with SQLAlchemy ORM

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. **Clone the repository**
```bash
   git clone https://github.com/ContentGardeningStudio/expenses-api
   cd expenses-api
```

2. **Create virtual environment**
```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
   uv sync
```

4. **Run the application**
```bash
   fastapi dev src/expenses_api/main.py
```

5. **Access the API**
   - API: http://127.0.0.1:8000
   - Interactive docs: http://127.0.0.1:8000/docs
   - Alternative docs: http://127.0.0.1:8000/redoc

---

## 📂 Project Structure
```
expenses-api/
├── src/expenses_api/
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # Database operations
│   ├── security.py          # Authentication & password hashing
│   ├── settings.py          # Configuration management
│   ├── deps.py              # Dependency injection
│   ├── seed.py              # Database seeding script
│   └── routers/
│       ├── auth.py          # Authentication endpoints
│       ├── categories.py    # Category endpoints
│       └── expenses.py      # Expense endpoints
├── tests/
│   ├── conftest.py          # Test fixtures
│   ├── test_crud.py         # CRUD logic tests
│   └── test_routers.py      # API endpoint tests
├── pyproject.toml           # Project dependencies
├── README.md
└── CONTRIBUTING.md
```

---

## 🔑 Authentication

### Register a New User
```bash
POST /auth/register
Content-Type: application/json

{
  "username": "johndoe",
  "password": "securepass123"
}
```

### Login
```bash
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username=johndoe&password=securepass123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using the Token

Include the token in all protected endpoints:
```bash
Authorization: Bearer <your_access_token>
```

---

## 📡 API Endpoints

### Categories

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/categories` | List all categories | ✅ |
| POST | `/categories` | Create a new category | ✅ |
| DELETE | `/categories/{id}` | Delete a category | ✅ |

**Create Category Example:**
```json
POST /categories
{
  "name": "Groceries"
}
```

---

### Expenses

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/expenses` | List expenses (paginated) | ✅ |
| GET | `/expenses/{id}` | Get expense by ID | ✅ |
| POST | `/expenses` | Create a new expense | ✅ |
| DELETE | `/expenses/{id}` | Delete an expense | ✅ |

**Create Expense Example:**
```json
POST /expenses
{
  "category_id": 1,
  "amount": "125.50",
  "currency": "EUR",
  "name": "Weekly groceries"
}
```

**List Expenses with Filters:**
```bash
GET /expenses?page=1&size=20&category_id=1&min_amount=50&max_amount=200
```

**Query Parameters:**
- `page` - Page number (default: 1)
- `size` - Items per page (default: 50, max: 200)
- `category_id` - Filter by category
- `min_amount` - Minimum amount filter
- `max_amount` - Maximum amount filter

---

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=expenses_api

# Run specific test file
pytest tests/test_routers.py

# Run with verbose output
pytest -v
```

**Test Coverage Includes:**
- ✅ User registration and authentication
- ✅ JWT token generation and validation
- ✅ Category CRUD operations
- ✅ Expense CRUD operations
- ✅ Pagination and filtering
- ✅ Optimistic locking
- ✅ Error handling
- ✅ Database constraints

---

## 🗄️ Database

### Initialize Database

The database is automatically created on first run. Tables:
- `users` - User accounts
- `categories` - Expense categories
- `expenses` - Expense records

### Seed Sample Data
```bash
python -m expenses_api.seed
```

This creates:
- 15 random categories
- 200 sample expenses

---

## ⚙️ Configuration

Create a `.env` file in the project root:
```env
# Database
DATABASE_URL=sqlite:///./expenses.db

# Security
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Debug
DEBUG=True
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Modern web framework |
| **SQLAlchemy** | ORM for database operations |
| **Pydantic** | Data validation |
| **Argon2** | Password hashing |
| **Python-JOSE** | JWT token handling |
| **Pytest** | Testing framework |
| **UV** | Fast dependency management |
| **SQLite** | Lightweight database |

---

## 🗺️ Roadmap

### ✅ Phase 1 - Foundations (DONE)
- Base project structure
- User authentication
- Categories & expenses CRUD
- Database initialization
- Comprehensive tests

### 🔜 Phase 2 - Stability
- [ ] Custom error handling
- [ ] Enhanced validation rules
- [ ] Advanced pagination
- [ ] Structured logging
- [ ] Environment configuration

### 🚧 Phase 3 - Features
- [ ] Date range filtering
- [ ] Monthly/yearly reports
- [ ] Soft delete functionality
- [ ] CSV/Excel export
- [ ] Expense summaries

### 🔐 Phase 4 - Multi-tenancy
- [ ] User-specific data isolation
- [ ] Role-based permissions
- [ ] User → Categories → Expenses hierarchy

### 📦 Phase 5 - Deployment
- [ ] Docker containerization
- [ ] Production server setup (Gunicorn + Uvicorn)
- [ ] Cloud deployment (Railway, Render, Fly.io)
- [ ] CI/CD pipeline

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Steps:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the MIT License.

---

## 👨‍💻 Author

**Leonel Noan**  
Email: leonelnoan@contentgardening.com

---

## 🙏 Acknowledgments

- FastAPI for the excellent framework
- SQLAlchemy for robust ORM capabilities
- The Python community for amazing tools

---

## 📞 Support

- 📧 Email: leonelnoan@contentgardening.com
- 🐛 Issues: [GitHub Issues](https://github.com/ContentGardeningStudio/expenses-api/issues)
- 📖 Documentation: http://127.0.0.1:8000/docs

---

**Happy expense tracking! 💰📊**