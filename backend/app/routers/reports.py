"""Report generation router."""
import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.project import Project, SubProject
from app.models.budget import BudgetCategory, CostItem, Expenditure
from app.models.alert import AlertLog
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/reports", tags=["报表管理"])


@router.get("/monthly")
async def monthly_report(
    year: int = Query(...),
    month: int = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """生成月度考核报表数据"""
    start_date = datetime.date(year, month, 1)
    if month == 12:
        end_date = datetime.date(year + 1, 1, 1)
    else:
        end_date = datetime.date(year, month + 1, 1)

    # Project overview
    proj_result = await db.execute(select(Project).order_by(Project.id).limit(1))
    project = proj_result.scalar_one_or_none()

    # Monthly expenditures
    monthly_exp = await db.execute(
        select(func.coalesce(func.sum(Expenditure.amount), 0))
        .where(Expenditure.record_date >= start_date, Expenditure.record_date < end_date)
    )
    monthly_total = float(monthly_exp.scalar())

    # Cumulative expenditures (up to end of this month)
    cum_exp = await db.execute(
        select(func.coalesce(func.sum(Expenditure.amount), 0))
        .where(Expenditure.record_date < end_date)
    )
    cumulative_total = float(cum_exp.scalar())

    # Sub-project details
    sp_result = await db.execute(select(SubProject).order_by(SubProject.sort_order, SubProject.id))
    sub_projects = sp_result.scalars().all()

    sp_details = []
    for sp in sub_projects:
        # Monthly spend for this sub-project
        sp_monthly = await db.execute(
            select(func.coalesce(func.sum(Expenditure.amount), 0))
            .where(
                Expenditure.sub_project_id == sp.id,
                Expenditure.record_date >= start_date,
                Expenditure.record_date < end_date,
            )
        )
        sp_month_spent = float(sp_monthly.scalar())

        # Budget variance
        budget_variance = sp.allocated_budget - sp.actual_spent if sp.allocated_budget else 0
        budget_usage_rate = (sp.actual_spent / sp.allocated_budget * 100) if sp.allocated_budget > 0 else 0

        # Schedule variance
        schedule_status = "正常"
        if sp.planned_end and sp.planned_start:
            total_days = (sp.planned_end - sp.planned_start).days or 1
            elapsed_days = (min(end_date, sp.planned_end) - sp.planned_start).days
            expected_progress = min(100, max(0, elapsed_days / total_days * 100))
            if sp.progress_percent < expected_progress - 10:
                schedule_status = "滞后"
            elif sp.progress_percent > expected_progress + 10:
                schedule_status = "超前"

        sp_details.append({
            "id": sp.id,
            "name": sp.name,
            "category": sp.category,
            "allocated_budget": sp.allocated_budget,
            "cumulative_spent": sp.actual_spent,
            "monthly_spent": sp_month_spent,
            "budget_remaining": budget_variance,
            "budget_usage_rate": round(budget_usage_rate, 2),
            "progress_percent": sp.progress_percent,
            "status": sp.status,
            "schedule_status": schedule_status,
            "risk_level": "red" if budget_usage_rate >= 90 else ("yellow" if budget_usage_rate >= 80 else "green"),
        })

    # Category summary
    cat_result = await db.execute(select(BudgetCategory).where(BudgetCategory.level == 1).order_by(BudgetCategory.sort_order))
    categories = cat_result.scalars().all()
    cat_summary = []
    for cat in categories:
        cat_monthly = await db.execute(
            select(func.coalesce(func.sum(Expenditure.amount), 0))
            .where(
                Expenditure.category_id == cat.id,
                Expenditure.record_date >= start_date,
                Expenditure.record_date < end_date,
            )
        )
        cat_cumulative = await db.execute(
            select(func.coalesce(func.sum(Expenditure.amount), 0))
            .where(Expenditure.category_id == cat.id, Expenditure.record_date < end_date)
        )
        monthly_val = float(cat_monthly.scalar())
        cumulative_val = float(cat_cumulative.scalar())
        cat_summary.append({
            "name": cat.name,
            "budget": cat.budget_amount,
            "monthly_spent": monthly_val,
            "cumulative_spent": cumulative_val,
            "usage_rate": round(cumulative_val / cat.budget_amount * 100, 2) if cat.budget_amount > 0 else 0,
        })

    # Alerts summary
    if month < 12:
        alert_end = datetime.datetime(year, month + 1, 1)
    else:
        alert_end = datetime.datetime(year + 1, 1, 1)
    alerts_result = await db.execute(
        select(AlertLog).where(
            AlertLog.created_at >= datetime.datetime(year, month, 1),
            AlertLog.created_at < alert_end,
        )
    )
    alerts = alerts_result.scalars().all()

    # Next month forecast (simple linear projection)
    prev_month_exp = await db.execute(
        select(func.coalesce(func.sum(Expenditure.amount), 0))
        .where(
            Expenditure.record_date >= start_date - datetime.timedelta(days=30),
            Expenditure.record_date < start_date,
        )
    )
    prev_total = float(prev_month_exp.scalar())
    forecast_next = (monthly_total + prev_total) / 2 if prev_total > 0 else monthly_total

    total_budget = project.total_budget if project else 56397.84
    reserve_rate = project.reserve_rate if project else 0.07

    return {
        "report_period": f"{year}年{month}月",
        "generated_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "overview": {
            "total_budget": total_budget,
            "reserve_budget": total_budget * reserve_rate,
            "usable_budget": total_budget * (1 - reserve_rate),
            "monthly_spent": monthly_total,
            "cumulative_spent": cumulative_total,
            "budget_remaining": total_budget - cumulative_total,
            "budget_usage_rate": round(cumulative_total / total_budget * 100, 2),
        },
        "sub_projects": sp_details,
        "category_summary": cat_summary,
        "alerts_count": {
            "total": len(alerts),
            "red": sum(1 for a in alerts if a.level == "red"),
            "yellow": sum(1 for a in alerts if a.level == "yellow"),
        },
        "forecast": {
            "next_month_estimated": round(forecast_next, 2),
            "remaining_months_budget": round((total_budget - cumulative_total) / max(1, monthly_total), 1) if monthly_total > 0 else None,
        },
        "recommendations": _generate_recommendations(sp_details, total_budget, cumulative_total, reserve_rate),
    }


@router.get("/export-data")
async def export_report_data(
    year: int = Query(...),
    month: int = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """导出月度报表数据（JSON格式，前端转Excel）"""
    # Reuse monthly report logic
    report = await monthly_report(year=year, month=month, db=db, user=user)
    return report


def _generate_recommendations(sp_details, total_budget, cumulative_spent, reserve_rate):
    """Generate automated recommendations based on data analysis."""
    recommendations = []

    over_budget_items = [sp for sp in sp_details if sp["risk_level"] == "red"]
    if over_budget_items:
        names = "、".join(sp["name"] for sp in over_budget_items[:3])
        recommendations.append(f"⚠️ 以下工程概算使用率超过90%，建议重点关注并控制支出：{names}")

    delayed_items = [sp for sp in sp_details if sp["schedule_status"] == "滞后"]
    if delayed_items:
        names = "、".join(sp["name"] for sp in delayed_items[:3])
        recommendations.append(f"⏰ 以下工程进度滞后，建议加大投入或调整计划：{names}")

    usage_rate = cumulative_spent / total_budget
    if usage_rate > (1 - reserve_rate):
        recommendations.append(f"💰 总体概算已超过可用概算线（{(1-reserve_rate)*100:.0f}%），正在使用弹性预备金")

    if not recommendations:
        recommendations.append("✅ 当前各项指标正常，请继续保持")

    return recommendations
