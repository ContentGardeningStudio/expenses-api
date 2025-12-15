# 📘 Expense API

A simple and clean **FastAPI** backend for managing expenses.

This project provides a standard architecture with modular routing, ORM models, database session management, and Pydantic schemas for validation.

---
## 🚀 Features

- ✅ CRUD for **categories**  
- ✅ CRUD for **expenses**  
- 🧩 Modular routing  
- 🗄 SQLAlchemy ORM models  
- 🔐 Pydantic validation  
- ⚡ Hot reload with `fastapi dev`  
- 📘 Automatic API documentation

## 📂 Project Structure

expenses-api/ │ 
            ├── pyproject.toml 
            ├── README.md 
            ├── src/
            │   └── expenses_api/
            │       ├── __init__.py
            │       ├── main.py             # Main FastAPI application entry point
            │       ├── database.py         # SQLAlchemy engine and session setup
            │       ├── models.py           # SQLAlchemy declarative base models (Category, Expense)
            │       ├── settings.py         # Pydantic-based configuration management
            │       ├── deps.py             # Database dependency injector (get_session)
            │       ├── schemas.py          # Pydantic request/response schemas
            │       ├── repositories.py     # Core database interaction (CRUD, Summaries)
            │       ├── routers/
            │       │   ├── categories.py   # Category API endpoints
            │       │   └── expenses.py     # Expense API endpoints
            │       └── seed.py             # Optional script for populating data
            └── tests/
            ├── test_repositories.py    
            └── test_routers.py         


---

## 🛠 Installation

### Clone the project

```bash
git clone [https://github.com/ContentGardeningStudio/expenses-api ](https://github.com/ContentGardeningStudio/expenses-api )

```
- Create a virtual environment using UV

```bash
uv venv
source .venv/bin/activate
```
- Install dependencies

```bash

uv sync

```

- Run the Application

```bash
fastapi dev src/expenses_api/main.py

```

📑 API Documentation

Once running:

Swagger UI http://127.0.0.1:8000/docs

➤ Create an Expense

POST /expenses

json

Copier le code

{

`  `"category\_id": 1,

`  `"amount": 23.50,

`  `"currency": "EUR",

`  `"occurred\_at": "2025-11-18T12:30:00",

`  `"note": "Lunch"

}

🧱 Tech Stack

Python 3.12+

FastAPI

SQLAlchemy

Pydantic

UV (fast environment & dependency management)

🗺 Roadmap

✅ Phase 1 — Foundations (DONE)

Base project structure

Categories & expenses CRUD

Database initialization

Routers, models, and schemas

🔜 Phase 2 — Improve Stability

` `Add custom error handling

` `Add tighter validation rules

` `Add pagination

` `Add logging config

` `Add .env settings

🚧 Phase 3 — Business Features

` `Filtering (by date, category, month)

` `Summaries (totals, monthly reports)

` `Soft delete

` `CSV/Excel export

🔐 Phase 4 — Authentication

` `JWT authentication

` `Users & permissions

` `User → categories → expenses hierarchy

📦 Phase 5 — Deployment

` `Dockerfile + docker-compose

` `Production server (Gunicorn + Uvicorn)

` `Deploy (Railway, Render, Fly.io)

` `CI/CD pipeline

🙌 Contributing

Issues, feature ideas, and pull requests are welcome!
