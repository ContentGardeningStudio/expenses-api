from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from expenses_api.database import engine, Base
from sqlalchemy.orm import Session
from .deps import get_session
from . import models
from .routers import categories


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")
    yield
    print("Application shutting down.")

app = FastAPI(title="Expenses API", lifespan=lifespan)

app.include_router(categories.router, prefix="/categories",
                   tags=["Categories"])


@app.get("/health")
def health():
    return {"status": "ok"}
