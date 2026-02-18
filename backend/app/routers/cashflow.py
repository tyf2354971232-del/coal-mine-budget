"""Cash flow management router."""
import datetime
import io
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.cashflow import CashFlow
from app.schemas.cashflow import CashFlowCreate, CashFlowUpdate, CashFlowResponse, CashFlowSummary
from app.utils.security import get_current_user, require_role

router = APIRouter(prefix="/api/cashflow", tags=["现金流管理"])


@router.get("", response_model=list[CashFlowResponse])
async def list_cashflows(
    flow_type: str = Query(None),
    status: str = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    limit: int = Query(200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取现金流记录列表"""
    query = select(CashFlow)
    if flow_type:
        query = query.where(CashFlow.flow_type == flow_type)
    if status:
        query = query.where(CashFlow.status == status)
    if start_date:
        query = query.where(CashFlow.record_date >= start_date)
    if end_date:
        query = query.where(CashFlow.record_date <= end_date)
    query = query.order_by(CashFlow.record_date.desc()).limit(limit)
    result = await db.execute(query)
    return [CashFlowResponse.model_validate(cf) for cf in result.scalars().all()]


@router.post("", response_model=CashFlowResponse)
async def create_cashflow(
    req: CashFlowCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "leader", "department")),
):
    """创建现金流记录"""
    cf = CashFlow(**req.model_dump(), created_by=user.id)
    db.add(cf)
    await db.flush()
    await db.refresh(cf)
    return CashFlowResponse.model_validate(cf)


@router.put("/{cf_id}", response_model=CashFlowResponse)
async def update_cashflow(
    cf_id: int,
    req: CashFlowUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "leader")),
):
    """更新现金流记录"""
    result = await db.execute(select(CashFlow).where(CashFlow.id == cf_id))
    cf = result.scalar_one_or_none()
    if not cf:
        raise HTTPException(status_code=404, detail="记录不存在")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(cf, field, value)
    await db.flush()
    await db.refresh(cf)
    return CashFlowResponse.model_validate(cf)


@router.delete("/{cf_id}")
async def delete_cashflow(
    cf_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    """删除现金流记录"""
    result = await db.execute(select(CashFlow).where(CashFlow.id == cf_id))
    cf = result.scalar_one_or_none()
    if not cf:
        raise HTTPException(status_code=404, detail="记录不存在")
    await db.delete(cf)
    return {"message": "删除成功"}


@router.post("/{cf_id}/approve")
async def approve_cashflow(
    cf_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "leader")),
):
    """审批现金流记录"""
    result = await db.execute(select(CashFlow).where(CashFlow.id == cf_id))
    cf = result.scalar_one_or_none()
    if not cf:
        raise HTTPException(status_code=404, detail="记录不存在")
    cf.status = "approved"
    cf.approved_by = user.id
    return {"message": "审批通过"}


@router.get("/summary", response_model=CashFlowSummary)
async def cashflow_summary(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """现金流汇总统计"""
    inflow_result = await db.execute(
        select(func.coalesce(func.sum(CashFlow.amount), 0))
        .where(CashFlow.flow_type == "inflow", CashFlow.status != "cancelled")
    )
    total_inflow = float(inflow_result.scalar())

    outflow_result = await db.execute(
        select(func.coalesce(func.sum(CashFlow.amount), 0))
        .where(CashFlow.flow_type == "outflow", CashFlow.status != "cancelled")
    )
    total_outflow = float(outflow_result.scalar())

    pending_result = await db.execute(
        select(func.count(CashFlow.id)).where(CashFlow.status == "pending")
    )
    pending_count = pending_result.scalar() or 0

    monthly_query = select(
        func.strftime('%Y-%m', CashFlow.record_date).label('month'),
        CashFlow.flow_type,
        func.sum(CashFlow.amount).label('amount'),
    ).where(CashFlow.status != "cancelled").group_by('month', CashFlow.flow_type).order_by('month')
    monthly_result = await db.execute(monthly_query)

    monthly_map = {}
    for r in monthly_result.all():
        if r.month not in monthly_map:
            monthly_map[r.month] = {"month": r.month, "inflow": 0, "outflow": 0}
        monthly_map[r.month][r.flow_type] = float(r.amount)

    monthly_data = sorted(monthly_map.values(), key=lambda x: x["month"])

    return CashFlowSummary(
        total_inflow=total_inflow,
        total_outflow=total_outflow,
        net_amount=total_inflow - total_outflow,
        pending_count=pending_count,
        monthly_data=monthly_data,
    )


@router.get("/export")
async def export_cashflow(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """导出现金流数据为Excel"""
    try:
        from openpyxl import Workbook
    except ImportError:
        from io import StringIO
        import json
        result = await db.execute(select(CashFlow).order_by(CashFlow.record_date.desc()))
        records = result.scalars().all()
        data = []
        for cf in records:
            data.append({
                "日期": str(cf.record_date),
                "类型": "流入(拨款)" if cf.flow_type == "inflow" else "流出(支出)",
                "金额(万元)": cf.amount,
                "收款方": cf.payee or "",
                "用途": cf.category or "",
                "说明": cf.description or "",
                "凭证号": cf.voucher_no or "",
                "状态": cf.status,
            })
        content = json.dumps(data, ensure_ascii=False, indent=2)
        return StreamingResponse(
            io.BytesIO(content.encode("utf-8")),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=cashflow_export.json"},
        )

    wb = Workbook()
    ws = wb.active
    ws.title = "现金流记录"
    headers = ["日期", "类型", "金额(万元)", "收款方", "用途", "说明", "凭证号", "状态"]
    ws.append(headers)

    result = await db.execute(select(CashFlow).order_by(CashFlow.record_date.desc()))
    for cf in result.scalars().all():
        ws.append([
            str(cf.record_date),
            "流入(拨款)" if cf.flow_type == "inflow" else "流出(支出)",
            cf.amount,
            cf.payee or "",
            cf.category or "",
            cf.description or "",
            cf.voucher_no or "",
            cf.status,
        ])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=cashflow_export.xlsx"},
    )
