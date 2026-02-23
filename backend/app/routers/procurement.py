"""Procurement, warehouse outbound, and civil settlement API routes."""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.project import SubProject
from app.models.procurement import (
    CivilSettlement, ProcurementMonthlySummary, ProcurementRecord, WarehouseOutbound,
)
from app.schemas.procurement import (
    CivilSettlementResponse, ProcurementMonthlySummaryResponse,
    ProcurementRecordResponse, WarehouseOutboundResponse,
    ProcurementStatsResponse, WarehouseOutboundStatsResponse,
    SettlementOverviewResponse,
)
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/settlement", tags=["决算数据"])


# ── Overview ──

@router.get("/overview", response_model=SettlementOverviewResponse)
async def settlement_overview(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """决算数据总览"""
    civil_q = await db.execute(
        select(func.coalesce(func.sum(CivilSettlement.settlement_amount), 0), func.count(CivilSettlement.id))
    )
    civil_row = civil_q.one()

    proc_q = await db.execute(
        select(func.coalesce(func.sum(ProcurementMonthlySummary.amount_somoni), 0))
    )
    proc_total = float(proc_q.scalar())

    proc_count_q = await db.execute(select(func.count(ProcurementRecord.id)))
    proc_count = proc_count_q.scalar()

    wh_q = await db.execute(
        select(func.coalesce(func.sum(WarehouseOutbound.amount), 0), func.count(WarehouseOutbound.id))
    )
    wh_row = wh_q.one()

    return SettlementOverviewResponse(
        civil_total=float(civil_row[0]),
        civil_items=civil_row[1],
        procurement_total_somoni=proc_total,
        procurement_records=proc_count,
        warehouse_total=float(wh_row[0]),
        warehouse_records=wh_row[1],
    )


# ── Civil Settlement ──

@router.get("/civil", response_model=list[CivilSettlementResponse])
async def list_civil_settlements(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """查询土建工程决算数据"""
    result = await db.execute(select(CivilSettlement).order_by(CivilSettlement.seq))
    settlements = result.scalars().all()

    responses = []
    for s in settlements:
        sp_name = None
        budget_amount = None
        if s.sub_project_id:
            sp_q = await db.execute(select(SubProject).where(SubProject.id == s.sub_project_id))
            sp = sp_q.scalar_one_or_none()
            if sp:
                sp_name = sp.name
                budget_amount = sp.allocated_budget * 10000

        responses.append(CivilSettlementResponse(
            id=s.id,
            seq=s.seq,
            project_name=s.project_name,
            audit_amount=s.audit_amount,
            settlement_amount=s.settlement_amount,
            payment_plan=s.payment_plan,
            somoni_amount=s.somoni_amount,
            somoni_40_percent=s.somoni_40_percent,
            feb_plan_somoni=s.feb_plan_somoni,
            debt_somoni=s.debt_somoni,
            contractor=s.contractor,
            sub_project_id=s.sub_project_id,
            sub_project_name=sp_name,
            budget_amount=budget_amount,
            note=s.note,
        ))
    return responses


# ── Procurement ──

@router.get("/procurement/monthly", response_model=list[ProcurementMonthlySummaryResponse])
async def list_procurement_monthly(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """查询塔国采购月度汇总"""
    result = await db.execute(
        select(ProcurementMonthlySummary).order_by(ProcurementMonthlySummary.month)
    )
    return [ProcurementMonthlySummaryResponse.model_validate(r) for r in result.scalars().all()]


@router.get("/procurement/records", response_model=list[ProcurementRecordResponse])
async def list_procurement_records(
    month: Optional[int] = Query(None, ge=1, le=12),
    project_name: Optional[str] = Query(None),
    material_name: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """查询塔国采购明细（支持按月份、工程名称、物资名称筛选）"""
    query = select(ProcurementRecord)
    if month:
        query = query.where(ProcurementRecord.month == month)
    if project_name:
        query = query.where(ProcurementRecord.project_name.contains(project_name))
    if material_name:
        query = query.where(ProcurementRecord.material_name.contains(material_name))

    query = query.order_by(ProcurementRecord.month, ProcurementRecord.seq)
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return [ProcurementRecordResponse.model_validate(r) for r in result.scalars().all()]


@router.get("/procurement/records/count")
async def count_procurement_records(
    month: Optional[int] = Query(None, ge=1, le=12),
    project_name: Optional[str] = Query(None),
    material_name: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取采购明细总数"""
    query = select(func.count(ProcurementRecord.id))
    if month:
        query = query.where(ProcurementRecord.month == month)
    if project_name:
        query = query.where(ProcurementRecord.project_name.contains(project_name))
    if material_name:
        query = query.where(ProcurementRecord.material_name.contains(material_name))
    result = await db.execute(query)
    return {"total": result.scalar()}


@router.get("/procurement/stats", response_model=ProcurementStatsResponse)
async def procurement_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """采购统计概览"""
    somoni_q = await db.execute(
        select(func.coalesce(func.sum(ProcurementRecord.purchase_amount_somoni), 0))
    )
    total_somoni = float(somoni_q.scalar())

    rmb_q = await db.execute(
        select(func.coalesce(func.sum(ProcurementRecord.amount_rmb), 0))
    )
    total_rmb = float(rmb_q.scalar())

    count_q = await db.execute(select(func.count(ProcurementRecord.id)))
    total_records = count_q.scalar()

    monthly_q = await db.execute(
        select(ProcurementMonthlySummary).order_by(ProcurementMonthlySummary.month)
    )
    monthly = [ProcurementMonthlySummaryResponse.model_validate(r) for r in monthly_q.scalars().all()]

    return ProcurementStatsResponse(
        total_somoni=total_somoni,
        total_rmb=total_rmb,
        total_records=total_records,
        monthly_data=monthly,
    )


# ── Warehouse Outbound ──

@router.get("/warehouse/outbound", response_model=list[WarehouseOutboundResponse])
async def list_warehouse_outbound(
    team: Optional[str] = Query(None),
    project_name: Optional[str] = Query(None),
    material_name: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """查询来塔物资出库明细"""
    query = select(WarehouseOutbound)
    if team:
        query = query.where(WarehouseOutbound.team.contains(team))
    if project_name:
        query = query.where(WarehouseOutbound.project_name.contains(project_name))
    if material_name:
        query = query.where(WarehouseOutbound.material_name.contains(material_name))
    if start_date:
        query = query.where(WarehouseOutbound.apply_date >= start_date)
    if end_date:
        query = query.where(WarehouseOutbound.apply_date <= end_date)

    query = query.order_by(WarehouseOutbound.apply_date.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return [WarehouseOutboundResponse.model_validate(r) for r in result.scalars().all()]


@router.get("/warehouse/outbound/count")
async def count_warehouse_outbound(
    team: Optional[str] = Query(None),
    project_name: Optional[str] = Query(None),
    material_name: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取出库明细总数"""
    query = select(func.count(WarehouseOutbound.id))
    if team:
        query = query.where(WarehouseOutbound.team.contains(team))
    if project_name:
        query = query.where(WarehouseOutbound.project_name.contains(project_name))
    if material_name:
        query = query.where(WarehouseOutbound.material_name.contains(material_name))
    if start_date:
        query = query.where(WarehouseOutbound.apply_date >= start_date)
    if end_date:
        query = query.where(WarehouseOutbound.apply_date <= end_date)
    result = await db.execute(query)
    return {"total": result.scalar()}


@router.get("/warehouse/outbound/stats", response_model=WarehouseOutboundStatsResponse)
async def warehouse_outbound_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """出库统计概览"""
    total_q = await db.execute(
        select(func.coalesce(func.sum(WarehouseOutbound.amount), 0))
    )
    total_amount = float(total_q.scalar())

    count_q = await db.execute(select(func.count(WarehouseOutbound.id)))
    total_records = count_q.scalar()

    team_q = await db.execute(
        select(
            WarehouseOutbound.team,
            func.sum(WarehouseOutbound.amount).label("total"),
            func.count(WarehouseOutbound.id).label("count"),
        ).group_by(WarehouseOutbound.team).order_by(func.sum(WarehouseOutbound.amount).desc())
    )
    team_summary = [
        {"team": r.team, "total": float(r.total or 0), "count": r.count}
        for r in team_q.all()
    ]

    return WarehouseOutboundStatsResponse(
        total_amount=total_amount,
        total_records=total_records,
        team_summary=team_summary,
    )
