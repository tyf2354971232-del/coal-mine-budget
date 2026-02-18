"""Alert management router."""
import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from app.database import get_db
from app.models.user import User
from app.models.project import Project, SubProject
from app.models.budget import BudgetCategory, CostItem, Expenditure
from app.models.alert import AlertLog
from app.utils.security import get_current_user, require_role
from app.config import settings

router = APIRouter(prefix="/api/alerts", tags=["预警管理"])


@router.get("", response_model=list)
async def list_alerts(
    level: str = Query(None),
    is_resolved: bool = Query(None),
    limit: int = Query(50),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取预警列表"""
    query = select(AlertLog)
    if level:
        query = query.where(AlertLog.level == level)
    if is_resolved is not None:
        query = query.where(AlertLog.is_resolved == is_resolved)
    query = query.order_by(AlertLog.created_at.desc()).limit(limit)
    result = await db.execute(query)
    return [
        {
            "id": a.id,
            "alert_type": a.alert_type,
            "level": a.level,
            "title": a.title,
            "message": a.message,
            "related_type": a.related_type,
            "related_id": a.related_id,
            "related_name": a.related_name,
            "is_read": a.is_read,
            "is_resolved": a.is_resolved,
            "created_at": a.created_at.strftime('%Y-%m-%d %H:%M:%S') if a.created_at else None,
            "resolved_at": a.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if a.resolved_at else None,
        }
        for a in result.scalars().all()
    ]


@router.post("/check")
async def run_alert_check(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "leader")),
):
    """手动触发预警检查（去重：同类型+同关联对象的未解决预警不会重复创建）"""
    alerts_generated = []
    alerts_updated = []

    # Helper: check if an unresolved alert of same type+target already exists
    async def _find_existing(alert_type: str, related_type: str, related_id: int):
        result = await db.execute(
            select(AlertLog).where(
                AlertLog.alert_type == alert_type,
                AlertLog.related_type == related_type,
                AlertLog.related_id == related_id,
                AlertLog.is_resolved == False,
            ).order_by(AlertLog.created_at.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    # 1. Check budget overrun for sub-projects
    sp_result = await db.execute(select(SubProject).where(SubProject.allocated_budget > 0))
    for sp in sp_result.scalars().all():
        ratio = sp.actual_spent / sp.allocated_budget if sp.allocated_budget > 0 else 0
        if ratio >= settings.ALERT_RED_THRESHOLD:
            existing = await _find_existing("budget_overrun", "sub_project", sp.id)
            msg = f"子工程「{sp.name}」概算使用率已达 {ratio*100:.1f}%，概算 {sp.allocated_budget:.2f}万元，已支出 {sp.actual_spent:.2f}万元"
            if existing:
                existing.level = "red"
                existing.message = msg
                alerts_updated.append(existing.title)
            else:
                alert = AlertLog(
                    alert_type="budget_overrun", level="red",
                    title="概算严重超支预警", message=msg,
                    related_type="sub_project", related_id=sp.id, related_name=sp.name,
                )
                db.add(alert)
                alerts_generated.append(alert.title)
        elif ratio >= settings.ALERT_YELLOW_THRESHOLD:
            existing = await _find_existing("budget_overrun", "sub_project", sp.id)
            msg = f"子工程「{sp.name}」概算使用率已达 {ratio*100:.1f}%，请注意控制支出"
            if existing:
                existing.level = "yellow"
                existing.message = msg
                alerts_updated.append(existing.title)
            else:
                alert = AlertLog(
                    alert_type="budget_overrun", level="yellow",
                    title="概算超支预警", message=msg,
                    related_type="sub_project", related_id=sp.id, related_name=sp.name,
                )
                db.add(alert)
                alerts_generated.append(alert.title)

    # 2. Check schedule delays
    today = datetime.date.today()
    sp_delay_result = await db.execute(
        select(SubProject).where(
            SubProject.planned_end != None,
            SubProject.status.in_(["in_progress", "not_started"]),
        )
    )
    for sp in sp_delay_result.scalars().all():
        if sp.planned_end and sp.planned_start:
            total_days = (sp.planned_end - sp.planned_start).days or 1
            elapsed_days = (today - sp.planned_start).days
            expected_progress = min(100, elapsed_days / total_days * 100)
            if expected_progress - sp.progress_percent > settings.PROGRESS_DELAY_THRESHOLD * 100:
                level = "yellow" if expected_progress - sp.progress_percent < 20 else "red"
                msg = f"子工程「{sp.name}」期望进度 {expected_progress:.1f}%，实际进度 {sp.progress_percent:.1f}%，落后 {expected_progress - sp.progress_percent:.1f}%"
                existing = await _find_existing("schedule_delay", "sub_project", sp.id)
                if existing:
                    existing.level = level
                    existing.message = msg
                    alerts_updated.append(existing.title)
                else:
                    alert = AlertLog(
                        alert_type="schedule_delay", level=level,
                        title="工期延误预警", message=msg,
                        related_type="sub_project", related_id=sp.id, related_name=sp.name,
                    )
                    db.add(alert)
                    alerts_generated.append(alert.title)

    # 3. Check burn rate (monthly consumption rate)
    proj_result = await db.execute(select(Project).order_by(Project.id).limit(1))
    project = proj_result.scalar_one_or_none()
    if project and project.end_date:
        remaining_months = max(1, (project.end_date - today).days / 30)
        total_spent_result = await db.execute(select(func.coalesce(func.sum(Expenditure.amount), 0)))
        total_spent = float(total_spent_result.scalar())

        # Average monthly burn
        first_exp_result = await db.execute(select(func.min(Expenditure.record_date)))
        first_date = first_exp_result.scalar()
        if first_date:
            months_elapsed = max(1, (today - first_date).days / 30)
            monthly_burn = total_spent / months_elapsed
            projected_total = total_spent + monthly_burn * remaining_months

            if projected_total > project.total_budget:
                level = "red" if projected_total > project.total_budget * 1.1 else "yellow"
                msg = f"按当前月均消耗 {monthly_burn:.2f}万元/月，预计总支出将达 {projected_total:.2f}万元，超出概算 {projected_total - project.total_budget:.2f}万元"
                existing = await _find_existing("burn_rate", "project", project.id)
                if existing:
                    existing.level = level
                    existing.message = msg
                    alerts_updated.append(existing.title)
                else:
                    alert = AlertLog(
                        alert_type="burn_rate", level=level,
                        title="消耗速率预警", message=msg,
                        related_type="project", related_id=project.id, related_name=project.name,
                    )
                    db.add(alert)
                    alerts_generated.append(alert.title)

    await db.flush()
    return {
        "message": f"检查完成，新增 {len(alerts_generated)} 条预警，更新 {len(alerts_updated)} 条已有预警",
        "new_alerts": alerts_generated,
        "updated_alerts": alerts_updated,
    }


@router.put("/{alert_id}/read")
async def mark_alert_read(alert_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """标记预警为已读"""
    result = await db.execute(select(AlertLog).where(AlertLog.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="预警不存在")
    alert.is_read = True
    return {"message": "已标记为已读"}


@router.put("/{alert_id}/resolve")
async def resolve_alert(alert_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(require_role("admin", "leader"))):
    """标记预警为已解决"""
    result = await db.execute(select(AlertLog).where(AlertLog.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="预警不存在")
    alert.is_resolved = True
    alert.resolved_at = datetime.datetime.utcnow()
    return {"message": "已标记为已解决"}


@router.get("/stats")
async def alert_stats(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """预警统计"""
    total = await db.execute(select(func.count(AlertLog.id)))
    unresolved = await db.execute(
        select(func.count(AlertLog.id)).where(AlertLog.is_resolved == False)
    )
    red_count = await db.execute(
        select(func.count(AlertLog.id)).where(AlertLog.level == "red", AlertLog.is_resolved == False)
    )
    yellow_count = await db.execute(
        select(func.count(AlertLog.id)).where(AlertLog.level == "yellow", AlertLog.is_resolved == False)
    )
    return {
        "total": total.scalar(),
        "unresolved": unresolved.scalar(),
        "red": red_count.scalar(),
        "yellow": yellow_count.scalar(),
    }
