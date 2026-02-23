"""Schemas for procurement, warehouse outbound, and civil settlement."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from app.schemas.types import FormattedDatetime


class CivilSettlementResponse(BaseModel):
    id: int
    seq: int
    project_name: str
    audit_amount: Optional[float] = None
    settlement_amount: float
    payment_plan: Optional[float] = None
    somoni_amount: Optional[float] = None
    somoni_40_percent: Optional[float] = None
    feb_plan_somoni: Optional[float] = None
    debt_somoni: Optional[float] = None
    contractor: Optional[str] = None
    sub_project_id: Optional[int] = None
    sub_project_name: Optional[str] = None
    budget_amount: Optional[float] = None
    note: Optional[str] = None

    class Config:
        from_attributes = True


class ProcurementMonthlySummaryResponse(BaseModel):
    id: int
    month: int
    amount_somoni: float

    class Config:
        from_attributes = True


class ProcurementRecordResponse(BaseModel):
    id: int
    month: int
    seq: Optional[int]
    material_name: str
    specification: Optional[str]
    unit: Optional[str]
    plan_price: Optional[float]
    plan_quantity: Optional[float]
    purchase_unit_price_somoni: Optional[float]
    purchase_method: Optional[str]
    payment_method: Optional[str]
    purchase_quantity: Optional[float]
    purchase_amount_somoni: Optional[float]
    stock_quantity: Optional[float]
    unit_price_rmb: Optional[float]
    amount_rmb: Optional[float]
    usage_unit: Optional[str]
    project_name: Optional[str]

    class Config:
        from_attributes = True


class WarehouseOutboundResponse(BaseModel):
    id: int
    team: Optional[str]
    apply_date: Optional[date]
    material_type: Optional[str]
    material_code: Optional[str]
    material_name: str
    specification: Optional[str]
    unit: Optional[str]
    quantity: Optional[float]
    unit_price: Optional[float]
    amount: Optional[float]
    usage_unit: Optional[str]
    project_name: Optional[str]

    class Config:
        from_attributes = True


class ProcurementStatsResponse(BaseModel):
    total_somoni: float
    total_rmb: float
    total_records: int
    monthly_data: List[ProcurementMonthlySummaryResponse]


class WarehouseOutboundStatsResponse(BaseModel):
    total_amount: float
    total_records: int
    team_summary: List[dict]


class SettlementOverviewResponse(BaseModel):
    civil_total: float
    civil_items: int
    procurement_total_somoni: float
    procurement_records: int
    warehouse_total: float
    warehouse_records: int
