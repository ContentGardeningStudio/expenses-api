from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from expenses_api.database import engine, Base
from sqlalchemy.orm import Session
from .deps import get_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")
    yield
    print("Application shutting down.")

app = FastAPI(title="Expenses API", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/debug-db")
def debug_db(db: Session = Depends(get_session)):
    try:
        count = db.query(Category).count()
        return {"db_connected": True, "categories": count}
    except Exception as e:
        return {"db_connected": False, "error": str(e)}
