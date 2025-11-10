from typing import Generator
from .database import SessionLocal


def get_session() -> Generator:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()
