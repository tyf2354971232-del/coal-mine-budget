"""Simulation schemas."""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.schemas.types import FormattedDatetime


class WhatIfParam(BaseModel):
    """Parameter for what-if analysis."""
    target_type: str  # sub_project, cost_item, category
    target_id: int
    field: str  # allocated_budget, unit_price, quantity, duration_days
    adjustment_type: str  # percent, absolute
    adjustment_value: float  # e.g., +10 for 10% increase or +100 for absolute increase


class WhatIfRequest(BaseModel):
    """What-if analysis request."""
    parameters: List[WhatIfParam]


class WhatIfResult(BaseModel):
    """Result of what-if analysis."""
    original_total_cost: float
    adjusted_total_cost: float
    cost_change: float
    cost_change_percent: float
    affected_items: List[Dict[str, Any]]
    budget_status: str  # within_budget, near_limit, over_budget
    reserve_impact: Dict[str, Any]
    kpi_impact: Dict[str, Any]


class ScenarioCreate(BaseModel):
    """Create a simulation scenario."""
    name: str
    description: Optional[str] = None
    parameters: Dict[str, Any]  # e.g., {"budget_factor": 0.9, "duration_factor": 1.1}


class SimulationCreate(BaseModel):
    """Create a new simulation."""
    name: str
    description: Optional[str] = None
    sim_type: str  # whatif, scenario, sensitivity
    scenarios: List[ScenarioCreate] = []


class ScenarioResponse(BaseModel):
    id: int
    simulation_id: int
    name: str
    description: Optional[str]
    parameters: Optional[Dict[str, Any]]
    results: Optional[Dict[str, Any]]
    total_cost: Optional[float]
    total_return: Optional[float]
    roi: Optional[float]
    created_at: FormattedDatetime

    class Config:
        from_attributes = True


class SimulationResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    sim_type: str
    created_by: Optional[int]
    created_at: FormattedDatetime
    scenarios: List[ScenarioResponse] = []

    class Config:
        from_attributes = True


class SensitivityRequest(BaseModel):
    """Sensitivity analysis request."""
    target_items: List[Dict[str, Any]]  # List of {type, id, field, range_min, range_max, steps}


class SensitivityResult(BaseModel):
    """Sensitivity analysis result for tornado chart."""
    items: List[Dict[str, Any]]  # [{name, field, low_impact, high_impact, base_value}]
    base_total_cost: float


class DashboardSummary(BaseModel):
    """Dashboard overview data."""
    total_budget: float
    total_spent: float
    budget_usage_rate: float
    reserve_budget: float
    reserve_used: float
    sub_project_count: int
    completed_count: int
    in_progress_count: int
    delayed_count: int
    overall_progress: float
    category_breakdown: List[Dict[str, Any]]
    top_risks: List[Dict[str, Any]]
    monthly_trend: List[Dict[str, Any]]
    kpi: Dict[str, Any]
    cash_outflow_total: float = 0
    cash_inflow_total: float = 0
    cash_balance: float = 0
    monthly_cashflow: List[Dict[str, Any]] = []
