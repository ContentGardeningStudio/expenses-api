from pydantic import BaseModel, condecimal, constr
from datetime import datetime
from typing import Optional


class CategoryCreate(BaseModel):
    name: constr(strip_whitespace=True, min_length=1, max_length=100)


class CategoryOut(BaseModel):
    id: int
    name: str
    created_at: datetime
    model_config = {"from_attributes": True}


class ExpenseCreate(BaseModel):
    category_id: int
    amount: condecimal(max_digits=12, decimal_places=2)
    currency: constr(min_length=3, max_length=3)
    occurred_at: datetime
    note: Optional[str] = None


class ExpenseOut(ExpenseCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class PaginatedExpenses(BaseModel):
    items: list[ExpenseOut]
    total: int
    page: int
    size: int
    model_config = {"from_attributes": True}
