"""Simulation and analysis router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.project import Project, SubProject
from app.models.budget import BudgetCategory, CostItem, Expenditure
from app.models.simulation import Simulation, SimScenario
from app.schemas.simulation import (
    WhatIfRequest, WhatIfResult,
    SimulationCreate, SimulationResponse,
    SensitivityRequest, SensitivityResult,
)
from app.utils.security import get_current_user, require_role

router = APIRouter(prefix="/api/simulation", tags=["模拟分析"])


@router.post("/whatif", response_model=WhatIfResult)
async def what_if_analysis(
    req: WhatIfRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """What-if 分析：调整参数查看对总体的影响"""
    # Get current totals
    proj_result = await db.execute(select(Project).order_by(Project.id).limit(1))
    project = proj_result.scalar_one_or_none()
    total_budget = project.total_budget if project else 56397.84

    # Use total allocated budget (sum of sub-project budgets) as the baseline cost
    # This is more meaningful than actual expenditures for "what-if" budget analysis
    allocated_result = await db.execute(
        select(func.coalesce(func.sum(SubProject.allocated_budget), 0))
    )
    original_total_cost = float(allocated_result.scalar())

    # Get all sub-projects for reference
    sp_result = await db.execute(select(SubProject))
    sub_projects = {sp.id: sp for sp in sp_result.scalars().all()}

    # Get all cost items for reference
    ci_result = await db.execute(select(CostItem))
    cost_items = {ci.id: ci for ci in ci_result.scalars().all()}

    adjusted_total_cost = original_total_cost
    affected_items = []

    for param in req.parameters:
        if param.target_type == "sub_project" and param.target_id in sub_projects:
            sp = sub_projects[param.target_id]
            original_val = getattr(sp, param.field, sp.allocated_budget)
            if param.adjustment_type == "percent":
                delta = original_val * (param.adjustment_value / 100)
            else:
                delta = param.adjustment_value
            adjusted_total_cost += delta
            affected_items.append({
                "type": "sub_project",
                "id": sp.id,
                "name": sp.name,
                "field": param.field,
                "original": original_val,
                "adjusted": original_val + delta,
                "delta": delta,
            })
        elif param.target_type == "cost_item" and param.target_id in cost_items:
            ci = cost_items[param.target_id]
            original_val = getattr(ci, param.field, ci.budget_amount)
            if param.adjustment_type == "percent":
                delta = original_val * (param.adjustment_value / 100)
            else:
                delta = param.adjustment_value
            adjusted_total_cost += delta
            affected_items.append({
                "type": "cost_item",
                "id": ci.id,
                "name": ci.name,
                "field": param.field,
                "original": original_val,
                "adjusted": original_val + delta,
                "delta": delta,
            })

    cost_change = adjusted_total_cost - original_total_cost
    cost_change_pct = (cost_change / original_total_cost * 100) if original_total_cost > 0 else 0
    reserve_rate = project.reserve_rate if project else 0.07
    usable_budget = total_budget * (1 - reserve_rate)

    if adjusted_total_cost > total_budget:
        budget_status = "over_budget"
    elif adjusted_total_cost > usable_budget:
        budget_status = "near_limit"
    else:
        budget_status = "within_budget"

    reserve_impact = {
        "total_reserve": round(total_budget * reserve_rate, 2),
        "reserve_needed": round(max(0, adjusted_total_cost - usable_budget), 2),
        "reserve_remaining": round(max(0, total_budget * reserve_rate - max(0, adjusted_total_cost - usable_budget)), 2),
    }

    kpi_impact = {
        "budget_control_rate": round((1 - adjusted_total_cost / total_budget) * 100, 2),
        "cost_change_percent": round(cost_change_pct, 2),
        "original_budget_usage": round(original_total_cost / total_budget * 100, 2),
        "adjusted_budget_usage": round(adjusted_total_cost / total_budget * 100, 2),
    }

    return WhatIfResult(
        original_total_cost=round(original_total_cost, 2),
        adjusted_total_cost=round(adjusted_total_cost, 2),
        cost_change=round(cost_change, 2),
        cost_change_percent=round(cost_change_pct, 2),
        affected_items=affected_items,
        budget_status=budget_status,
        reserve_impact=reserve_impact,
        kpi_impact=kpi_impact,
    )


@router.post("/sensitivity", response_model=SensitivityResult)
async def sensitivity_analysis(
    req: SensitivityRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """敏感性分析：生成龙卷风图数据"""
    spent_result = await db.execute(select(func.coalesce(func.sum(Expenditure.amount), 0)))
    base_total_cost = float(spent_result.scalar())

    sp_result = await db.execute(select(SubProject))
    sub_projects = {sp.id: sp for sp in sp_result.scalars().all()}

    items = []
    for target in req.target_items:
        t_type = target.get("type", "sub_project")
        t_id = target.get("id")
        field = target.get("field", "allocated_budget")
        range_min = target.get("range_min", -20)
        range_max = target.get("range_max", 20)

        if t_type == "sub_project" and t_id in sub_projects:
            sp = sub_projects[t_id]
            base_val = getattr(sp, field, sp.allocated_budget)
            low_delta = base_val * (range_min / 100)
            high_delta = base_val * (range_max / 100)
            items.append({
                "name": sp.name,
                "field": field,
                "base_value": base_val,
                "low_value": base_val + low_delta,
                "high_value": base_val + high_delta,
                "low_impact": round(low_delta, 2),
                "high_impact": round(high_delta, 2),
                "low_total": round(base_total_cost + low_delta, 2),
                "high_total": round(base_total_cost + high_delta, 2),
            })

    # Sort by impact magnitude
    items.sort(key=lambda x: abs(x["high_impact"] - x["low_impact"]), reverse=True)

    return SensitivityResult(items=items, base_total_cost=base_total_cost)


@router.post("/scenarios", response_model=SimulationResponse)
async def create_scenario_comparison(
    req: SimulationCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """创建情景对比分析"""
    proj_result = await db.execute(select(Project).order_by(Project.id).limit(1))
    project = proj_result.scalar_one_or_none()
    total_budget = project.total_budget if project else 56397.84

    sim = Simulation(
        name=req.name,
        description=req.description,
        sim_type=req.sim_type,
        created_by=user.id,
    )
    db.add(sim)
    await db.flush()

    for sc in req.scenarios:
        budget_factor = sc.parameters.get("budget_factor", 1.0)
        duration_factor = sc.parameters.get("duration_factor", 1.0)
        efficiency_factor = sc.parameters.get("efficiency_factor", 1.0)

        adjusted_cost = total_budget * budget_factor
        estimated_return = total_budget * efficiency_factor * 1.2  # Simplified ROI model
        roi = (estimated_return - adjusted_cost) / adjusted_cost * 100 if adjusted_cost > 0 else 0

        scenario = SimScenario(
            simulation_id=sim.id,
            name=sc.name,
            description=sc.description,
            parameters=sc.parameters,
            results={
                "adjusted_total_budget": round(adjusted_cost, 2),
                "estimated_duration_months": round(12 * duration_factor, 1),
                "estimated_return": round(estimated_return, 2),
                "budget_savings": round(total_budget - adjusted_cost, 2),
                "efficiency_gain": round((efficiency_factor - 1) * 100, 2),
            },
            total_cost=round(adjusted_cost, 2),
            total_return=round(estimated_return, 2),
            roi=round(roi, 2),
        )
        db.add(scenario)

    await db.flush()
    await db.refresh(sim)

    # Explicitly load scenarios (avoid lazy-loading in async context)
    sc_result = await db.execute(
        select(SimScenario).where(SimScenario.simulation_id == sim.id)
    )
    scenario_list = sc_result.scalars().all()

    # Manually construct response to avoid triggering lazy-load on sim.scenarios
    return SimulationResponse(
        id=sim.id,
        name=sim.name,
        description=sim.description,
        sim_type=sim.sim_type,
        created_by=sim.created_by,
        created_at=sim.created_at,
        scenarios=[
            ScenarioResponse(
                id=s.id,
                simulation_id=s.simulation_id,
                name=s.name,
                description=s.description,
                parameters=s.parameters,
                results=s.results,
                total_cost=s.total_cost,
                total_return=s.total_return,
                roi=s.roi,
                created_at=s.created_at,
            )
            for s in scenario_list
        ],
    )


@router.get("/scenarios", response_model=list[SimulationResponse])
async def list_simulations(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取所有模拟分析"""
    result = await db.execute(select(Simulation).order_by(Simulation.created_at.desc()))
    sims = result.scalars().all()
    responses = []
    for sim in sims:
        sc_result = await db.execute(
            select(SimScenario).where(SimScenario.simulation_id == sim.id)
        )
        responses.append(SimulationResponse(
            id=sim.id,
            name=sim.name,
            description=sim.description,
            sim_type=sim.sim_type,
            created_by=sim.created_by,
            created_at=sim.created_at,
            scenarios=[
                ScenarioResponse(
                    id=s.id, simulation_id=s.simulation_id, name=s.name,
                    description=s.description, parameters=s.parameters,
                    results=s.results, total_cost=s.total_cost,
                    total_return=s.total_return, roi=s.roi, created_at=s.created_at,
                )
                for s in sc_result.scalars().all()
            ],
        ))
    return responses


@router.get("/scenarios/{sim_id}", response_model=SimulationResponse)
async def get_simulation(sim_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Simulation).where(Simulation.id == sim_id))
    sim = result.scalar_one_or_none()
    if not sim:
        raise HTTPException(status_code=404, detail="模拟不存在")
    sc_result = await db.execute(select(SimScenario).where(SimScenario.simulation_id == sim.id))
    return SimulationResponse(
        id=sim.id,
        name=sim.name,
        description=sim.description,
        sim_type=sim.sim_type,
        created_by=sim.created_by,
        created_at=sim.created_at,
        scenarios=[
            ScenarioResponse(
                id=s.id, simulation_id=s.simulation_id, name=s.name,
                description=s.description, parameters=s.parameters,
                results=s.results, total_cost=s.total_cost,
                total_return=s.total_return, roi=s.roi, created_at=s.created_at,
            )
            for s in sc_result.scalars().all()
        ],
    )


@router.delete("/scenarios/{sim_id}")
async def delete_simulation(
    sim_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "leader")),
):
    result = await db.execute(select(Simulation).where(Simulation.id == sim_id))
    sim = result.scalar_one_or_none()
    if not sim:
        raise HTTPException(status_code=404, detail="模拟不存在")
    await db.delete(sim)
    return {"message": "删除成功"}


# Import ScenarioResponse at module level to avoid issues
from app.schemas.simulation import ScenarioResponse
