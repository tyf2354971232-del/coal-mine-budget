"""Budget, cost item, and expenditure schemas."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class BudgetCategoryCreate(BaseModel):
    name: str
    code: Optional[str] = None
    parent_id: Optional[int] = None
    level: int = 1
    budget_amount: float = 0
    description: Optional[str] = None
    sort_order: int = 0


class BudgetCategoryUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    budget_amount: Optional[float] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None


class BudgetCategoryResponse(BaseModel):
    id: int
    name: str
    code: Optional[str]
    parent_id: Optional[int]
    level: int
    budget_amount: float
    description: Optional[str]
    sort_order: int
    actual_spent: float = 0
    children: List["BudgetCategoryResponse"] = []

    class Config:
        from_attributes = True


class CostItemCreate(BaseModel):
    sub_project_id: int
    category_id: Optional[int] = None
    name: str
    budget_amount: float = 0
    unit: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    note: Optional[str] = None


class CostItemUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    budget_amount: Optional[float] = None
    unit: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    note: Optional[str] = None


class CostItemResponse(BaseModel):
    id: int
    sub_project_id: int
    category_id: Optional[int]
    name: str
    budget_amount: float
    actual_amount: float
    unit: Optional[str]
    quantity: Optional[float]
    unit_price: Optional[float]
    note: Optional[str]
    usage_rate: float = 0

    class Config:
        from_attributes = True


class ExpenditureCreate(BaseModel):
    cost_item_id: Optional[int] = None
    sub_project_id: int
    category_id: Optional[int] = None
    record_date: date
    amount: float
    description: Optional[str] = None
    voucher_no: Optional[str] = None
    source: str = "manual"


class ExpenditureResponse(BaseModel):
    id: int
    cost_item_id: Optional[int]
    sub_project_id: int
    category_id: Optional[int]
    record_date: date
    amount: float
    description: Optional[str]
    voucher_no: Optional[str]
    source: str
    created_by: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class ExpenditureBatchImport(BaseModel):
    """Schema for batch importing expenditures from Excel."""
    records: List[ExpenditureCreate]
