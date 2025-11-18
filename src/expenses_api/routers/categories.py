from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..schemas import CategoryCreate, CategoryOut
from ..deps import get_session
from ..repositories import create_category, list_categories

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryOut])
def get_categories(db: Session = Depends(get_session)):
    return list_categories(db)


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def post_category(payload: CategoryCreate, db: Session = Depends(get_session)):
    existing = [c for c in list_categories(
        db) if c.name.lower() == payload.name.lower()]
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    return create_category(db, payload.name)
