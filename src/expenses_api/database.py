from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .settings import settings
from sqlalchemy.orm import declarative_base

engine = create_engine(settings.DATABASE_URL, echo=True, connect_args={
                       "check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
