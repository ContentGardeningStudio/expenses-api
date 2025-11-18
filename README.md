# 📘 Expense API

A simple and clean **FastAPI** backend for managing categories and expenses

This project provides a minimal architecture with modular routing, ORM models, database session management, and Pydantic schemas for validation.

---

## 📂 Project Structure

expenses-api/ │ 
              ├── pyproject.toml 
              ├── README.md 
              │ └── src/expenses_api/ 
                    ├── main.py 
                    ├── deps.py 
                    ├── database.py 
                    ├── models.py 
                    ├── schemas.py 
                    ├── routers/ 
                    │ ├── categories.py 
                    │ └── expenses.py 
                    └── init.py


---

## 🛠 Installation

### 1️⃣ Clone the project

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
