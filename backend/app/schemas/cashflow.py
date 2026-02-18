"""Cash flow schemas."""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date
from app.schemas.types import FormattedDatetime


class CashFlowCreate(BaseModel):
    project_id: int = 1
    flow_type: str  # outflow / inflow
    category: Optional[str] = None
    amount: float
    record_date: date
    payee: Optional[str] = None
    payment_method: Optional[str] = None
    description: Optional[str] = None
    voucher_no: Optional[str] = None
    related_sub_project_id: Optional[int] = None
    status: str = "paid"


class CashFlowUpdate(BaseModel):
    flow_type: Optional[str] = None
    category: Optional[str] = None
    amount: Optional[float] = None
    record_date: Optional[date] = None
    payee: Optional[str] = None
    payment_method: Optional[str] = None
    description: Optional[str] = None
    voucher_no: Optional[str] = None
    related_sub_project_id: Optional[int] = None
    status: Optional[str] = None


class CashFlowResponse(BaseModel):
    id: int
    project_id: int
    flow_type: str
    category: Optional[str]
    amount: float
    record_date: date
    payee: Optional[str]
    payment_method: Optional[str]
    description: Optional[str]
    voucher_no: Optional[str]
    related_sub_project_id: Optional[int]
    status: str
    approved_by: Optional[int]
    created_by: Optional[int]
    created_at: FormattedDatetime

    class Config:
        from_attributes = True


class CashFlowSummary(BaseModel):
    total_inflow: float
    total_outflow: float
    net_amount: float
    pending_count: int
    monthly_data: List[Dict[str, Any]]
