"""Project and sub-project schemas."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    total_budget: float
    reserve_rate: float = 0.07
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    total_budget: Optional[float] = None
    reserve_rate: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None


class SubProjectCreate(BaseModel):
    project_id: int
    name: str
    description: Optional[str] = None
    category: str
    allocated_budget: float = 0
    planned_start: Optional[date] = None
    planned_end: Optional[date] = None
    responsible_dept: Optional[str] = None
    sort_order: int = 0


class SubProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    allocated_budget: Optional[float] = None
    progress_percent: Optional[float] = None
    status: Optional[str] = None
    planned_start: Optional[date] = None
    planned_end: Optional[date] = None
    actual_start: Optional[date] = None
    actual_end: Optional[date] = None
    responsible_dept: Optional[str] = None
    sort_order: Optional[int] = None


class MilestoneCreate(BaseModel):
    sub_project_id: int
    name: str
    description: Optional[str] = None
    planned_date: Optional[date] = None
    sort_order: int = 0


class MilestoneUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    planned_date: Optional[date] = None
    actual_date: Optional[date] = None
    status: Optional[str] = None


class ProgressRecordCreate(BaseModel):
    sub_project_id: int
    record_date: date
    percent: float
    milestone: Optional[str] = None
    note: Optional[str] = None


class MilestoneResponse(BaseModel):
    id: int
    sub_project_id: int
    name: str
    description: Optional[str]
    planned_date: Optional[date]
    actual_date: Optional[date]
    status: str
    sort_order: int

    class Config:
        from_attributes = True


class ProgressRecordResponse(BaseModel):
    id: int
    sub_project_id: int
    record_date: date
    percent: float
    milestone: Optional[str]
    note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SubProjectResponse(BaseModel):
    id: int
    project_id: int
    name: str
    description: Optional[str]
    category: str
    allocated_budget: float
    actual_spent: float
    progress_percent: float
    status: str
    planned_start: Optional[date]
    planned_end: Optional[date]
    actual_start: Optional[date]
    actual_end: Optional[date]
    responsible_dept: Optional[str]
    sort_order: int
    budget_usage_rate: float = 0
    is_over_budget: bool = False
    schedule_variance: Optional[float] = None

    class Config:
        from_attributes = True


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    total_budget: float
    reserve_rate: float
    start_date: Optional[date]
    end_date: Optional[date]
    status: str
    created_at: datetime
    sub_projects: List[SubProjectResponse] = []

    class Config:
        from_attributes = True
