"""Dashboard router - the executive overview."""
from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.project import Project, SubProject
from app.models.budget import BudgetCategory, Expenditure, CostItem
from app.models.alert import AlertLog
from app.models.cashflow import CashFlow
from app.schemas.simulation import DashboardSummary
from app.utils.security import get_current_user
from app.config import settings

router = APIRouter(prefix="/api/dashboard", tags=["领导驾驶舱"])


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """获取驾驶舱总览数据"""
    # Get main project
    proj_result = await db.execute(select(Project).order_by(Project.id).limit(1))
    project = proj_result.scalar_one_or_none()

    total_budget = project.total_budget if project else settings.TOTAL_BUDGET
    reserve_rate = project.reserve_rate if project else settings.DEFAULT_RESERVE_RATE

    # Total spent
    spent_result = await db.execute(select(func.coalesce(func.sum(Expenditure.amount), 0)))
    total_spent = float(spent_result.scalar())

    # Reserve budget
    reserve_budget = total_budget * reserve_rate

    # Sub-project stats
    sp_result = await db.execute(select(SubProject))
    sub_projects = sp_result.scalars().all()
    sub_project_count = len(sub_projects)
    completed_count = sum(1 for sp in sub_projects if sp.status == "completed")
    in_progress_count = sum(1 for sp in sub_projects if sp.status == "in_progress")
    delayed_count = sum(1 for sp in sub_projects if sp.status == "delayed")

    # Overall progress (weighted by budget)
    total_allocated = sum(sp.allocated_budget for sp in sub_projects) or 1
    overall_progress = sum(sp.progress_percent * sp.allocated_budget for sp in sub_projects) / total_allocated

    # Category breakdown
    cat_result = await db.execute(select(BudgetCategory).where(BudgetCategory.level == 1).order_by(BudgetCategory.sort_order))
    categories = cat_result.scalars().all()
    category_breakdown = []
    for cat in categories:
        exp_result = await db.execute(
            select(func.coalesce(func.sum(Expenditure.amount), 0)).where(Expenditure.category_id == cat.id)
        )
        cat_spent = float(exp_result.scalar())
        # Also sum child categories
        child_result = await db.execute(
            select(BudgetCategory.id).where(BudgetCategory.parent_id == cat.id)
        )
        child_ids = [r[0] for r in child_result.all()]
        if child_ids:
            child_exp_result = await db.execute(
                select(func.coalesce(func.sum(Expenditure.amount), 0)).where(Expenditure.category_id.in_(child_ids))
            )
            cat_spent += float(child_exp_result.scalar())

        category_breakdown.append({
            "id": cat.id,
            "name": cat.name,
            "budget": cat.budget_amount,
            "spent": cat_spent,
            "usage_rate": round(cat_spent / cat.budget_amount * 100, 2) if cat.budget_amount > 0 else 0,
        })

    # Top risks (sub-projects with highest budget overrun risk)
    top_risks = []
    for sp in sorted(sub_projects, key=lambda s: (s.actual_spent / s.allocated_budget if s.allocated_budget > 0 else 0), reverse=True)[:5]:
        if sp.allocated_budget > 0:
            rate = sp.actual_spent / sp.allocated_budget
            top_risks.append({
                "id": sp.id,
                "name": sp.name,
                "budget": sp.allocated_budget,
                "spent": sp.actual_spent,
                "usage_rate": round(rate * 100, 2),
                "risk_level": "red" if rate >= 0.9 else ("yellow" if rate >= 0.8 else "green"),
            })

    # Monthly trend
    monthly_query = select(
        func.strftime('%Y-%m', Expenditure.record_date).label('month'),
        func.sum(Expenditure.amount).label('amount'),
    ).group_by('month').order_by('month')
    monthly_result = await db.execute(monthly_query)
    monthly_trend = [{"month": r.month, "amount": float(r.amount)} for r in monthly_result.all()]

    # KPI
    kpi = {
        "budget_control_rate": round((1 - total_spent / total_budget) * 100, 2) if total_budget > 0 else 100,
        "schedule_on_time_rate": round(
            (completed_count + in_progress_count) / sub_project_count * 100, 2
        ) if sub_project_count > 0 else 0,
        "cost_savings_rate": 0,  # To be calculated when baseline data available
        "efficiency_index": 0,  # To be calculated when production data available
    }

    # Cash flow summary
    cf_outflow = await db.execute(
        select(func.coalesce(func.sum(CashFlow.amount), 0))
        .where(CashFlow.flow_type == "outflow", CashFlow.status != "cancelled")
    )
    cash_outflow_total = float(cf_outflow.scalar())
    cf_inflow = await db.execute(
        select(func.coalesce(func.sum(CashFlow.amount), 0))
        .where(CashFlow.flow_type == "inflow", CashFlow.status != "cancelled")
    )
    cash_inflow_total = float(cf_inflow.scalar())

    cf_monthly = await db.execute(
        select(
            func.strftime('%Y-%m', CashFlow.record_date).label('month'),
            CashFlow.flow_type,
            func.sum(CashFlow.amount).label('amount'),
        ).where(CashFlow.status != "cancelled")
        .group_by('month', CashFlow.flow_type).order_by('month')
    )
    cf_map = {}
    for r in cf_monthly.all():
        if r.month not in cf_map:
            cf_map[r.month] = {"month": r.month, "inflow": 0, "outflow": 0}
        cf_map[r.month][r.flow_type] = float(r.amount)
    monthly_cashflow = sorted(cf_map.values(), key=lambda x: x["month"])

    return DashboardSummary(
        total_budget=total_budget,
        total_spent=total_spent,
        budget_usage_rate=round(total_spent / total_budget * 100, 2) if total_budget > 0 else 0,
        reserve_budget=reserve_budget,
        reserve_used=max(0, total_spent - (total_budget - reserve_budget)),
        sub_project_count=sub_project_count,
        completed_count=completed_count,
        in_progress_count=in_progress_count,
        delayed_count=delayed_count,
        overall_progress=round(overall_progress, 2),
        category_breakdown=category_breakdown,
        top_risks=top_risks,
        monthly_trend=monthly_trend,
        kpi=kpi,
        cash_outflow_total=cash_outflow_total,
        cash_inflow_total=cash_inflow_total,
        cash_balance=cash_inflow_total - cash_outflow_total,
        monthly_cashflow=monthly_cashflow,
    )


@router.get("/alerts")
async def get_recent_alerts(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取最近预警"""
    result = await db.execute(
        select(AlertLog).where(AlertLog.is_resolved == False).order_by(AlertLog.created_at.desc()).limit(limit)
    )
    alerts = result.scalars().all()
    return [
        {
            "id": a.id,
            "type": a.alert_type,
            "level": a.level,
            "title": a.title,
            "message": a.message,
            "related_name": a.related_name,
            "is_read": a.is_read,
            "created_at": a.created_at.strftime('%Y-%m-%d %H:%M:%S') if a.created_at else None,
        }
        for a in alerts
    ]
