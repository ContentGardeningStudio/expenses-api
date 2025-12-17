from fastapi import FastAPI
from contextlib import asynccontextmanager
from expenses_api.database import engine, Base
from .routers import categories, expenses, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")
    yield
    print("Application shutting down.")


app = FastAPI(title="Expenses API", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(expenses.router)


@app.get("/health")
def health():
    return {"status": "ok"}
