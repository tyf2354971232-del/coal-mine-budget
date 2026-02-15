"""Expenditure management router."""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.budget import Expenditure, CostItem
from app.models.project import SubProject
from app.schemas.budget import ExpenditureCreate, ExpenditureResponse, ExpenditureBatchImport
from app.utils.security import get_current_user, require_role

router = APIRouter(prefix="/api/expenditures", tags=["支出管理"])


@router.get("", response_model=list[ExpenditureResponse])
async def list_expenditures(
    sub_project_id: Optional[int] = Query(None),
    cost_item_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    source: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取支出记录列表（支持筛选、分页）"""
    query = select(Expenditure)
    if sub_project_id:
        query = query.where(Expenditure.sub_project_id == sub_project_id)
    if cost_item_id:
        query = query.where(Expenditure.cost_item_id == cost_item_id)
    if category_id:
        query = query.where(Expenditure.category_id == category_id)
    if start_date:
        query = query.where(Expenditure.record_date >= start_date)
    if end_date:
        query = query.where(Expenditure.record_date <= end_date)
    if source:
        query = query.where(Expenditure.source == source)

    query = query.order_by(Expenditure.record_date.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return [ExpenditureResponse.model_validate(e) for e in result.scalars().all()]


@router.get("/summary")
async def expenditure_summary(
    sub_project_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取支出汇总"""
    query = select(func.coalesce(func.sum(Expenditure.amount), 0))
    if sub_project_id:
        query = query.where(Expenditure.sub_project_id == sub_project_id)
    result = await db.execute(query)
    total = float(result.scalar())

    # Monthly breakdown
    monthly_query = select(
        func.strftime('%Y-%m', Expenditure.record_date).label('month'),
        func.sum(Expenditure.amount).label('amount'),
    )
    if sub_project_id:
        monthly_query = monthly_query.where(Expenditure.sub_project_id == sub_project_id)
    monthly_query = monthly_query.group_by('month').order_by('month')
    monthly_result = await db.execute(monthly_query)
    monthly = [{"month": r.month, "amount": float(r.amount)} for r in monthly_result.all()]

    return {"total": total, "monthly": monthly}


@router.post("", response_model=ExpenditureResponse)
async def create_expenditure(
    req: ExpenditureCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "leader", "department")),
):
    """录入支出"""
    exp = Expenditure(**req.model_dump(), created_by=user.id)
    db.add(exp)
    await db.flush()

    # Update cost item actual amount
    if req.cost_item_id:
        await _update_cost_item_total(db, req.cost_item_id)
    # Update sub-project actual spent
    await _update_sub_project_spent(db, req.sub_project_id)

    await db.refresh(exp)
    return ExpenditureResponse.model_validate(exp)


@router.post("/batch", response_model=dict)
async def batch_import_expenditures(
    req: ExpenditureBatchImport,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "leader", "department")),
):
    """批量导入支出记录"""
    count = 0
    sp_ids = set()
    ci_ids = set()

    for record in req.records:
        exp = Expenditure(**record.model_dump(), created_by=user.id)
        db.add(exp)
        sp_ids.add(record.sub_project_id)
        if record.cost_item_id:
            ci_ids.add(record.cost_item_id)
        count += 1

    await db.flush()

    # Update totals
    for ci_id in ci_ids:
        await _update_cost_item_total(db, ci_id)
    for sp_id in sp_ids:
        await _update_sub_project_spent(db, sp_id)

    return {"message": f"成功导入 {count} 条记录", "count": count}


@router.post("/upload-excel")
async def upload_excel(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "leader", "department")),
):
    """从Excel文件导入支出"""
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(status_code=400, detail="仅支持 .xlsx, .xls, .csv 文件")

    import pandas as pd
    from io import BytesIO

    content = await file.read()
    if file.filename.endswith('.csv'):
        df = pd.read_csv(BytesIO(content))
    else:
        df = pd.read_excel(BytesIO(content))

    required_cols = {'子工程ID', '日期', '金额'}
    if not required_cols.issubset(set(df.columns)):
        raise HTTPException(
            status_code=400,
            detail=f"Excel必须包含以下列: {required_cols}. 当前列: {list(df.columns)}"
        )

    count = 0
    sp_ids = set()
    errors = []

    for idx, row in df.iterrows():
        try:
            exp = Expenditure(
                sub_project_id=int(row['子工程ID']),
                record_date=pd.to_datetime(row['日期']).date(),
                amount=float(row['金额']),
                description=str(row.get('描述', '')),
                voucher_no=str(row.get('凭证号', '')) if pd.notna(row.get('凭证号')) else None,
                category_id=int(row['科目ID']) if pd.notna(row.get('科目ID')) else None,
                cost_item_id=int(row['成本项ID']) if pd.notna(row.get('成本项ID')) else None,
                source="excel_import",
                created_by=user.id,
            )
            db.add(exp)
            sp_ids.add(int(row['子工程ID']))
            count += 1
        except Exception as e:
            errors.append(f"第{idx + 2}行: {str(e)}")

    await db.flush()
    for sp_id in sp_ids:
        await _update_sub_project_spent(db, sp_id)

    return {"message": f"成功导入 {count} 条记录", "count": count, "errors": errors}


@router.delete("/{exp_id}")
async def delete_expenditure(
    exp_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    result = await db.execute(select(Expenditure).where(Expenditure.id == exp_id))
    exp = result.scalar_one_or_none()
    if not exp:
        raise HTTPException(status_code=404, detail="记录不存在")
    sp_id = exp.sub_project_id
    ci_id = exp.cost_item_id
    await db.delete(exp)
    await db.flush()
    if ci_id:
        await _update_cost_item_total(db, ci_id)
    await _update_sub_project_spent(db, sp_id)
    return {"message": "删除成功"}


async def _update_cost_item_total(db: AsyncSession, cost_item_id: int):
    """Recalculate cost item actual amount from expenditures."""
    result = await db.execute(
        select(func.coalesce(func.sum(Expenditure.amount), 0))
        .where(Expenditure.cost_item_id == cost_item_id)
    )
    total = float(result.scalar())
    ci_result = await db.execute(select(CostItem).where(CostItem.id == cost_item_id))
    ci = ci_result.scalar_one_or_none()
    if ci:
        ci.actual_amount = total


async def _update_sub_project_spent(db: AsyncSession, sub_project_id: int):
    """Recalculate sub-project actual spent from expenditures."""
    result = await db.execute(
        select(func.coalesce(func.sum(Expenditure.amount), 0))
        .where(Expenditure.sub_project_id == sub_project_id)
    )
    total = float(result.scalar())
    sp_result = await db.execute(select(SubProject).where(SubProject.id == sub_project_id))
    sp = sp_result.scalar_one_or_none()
    if sp:
        sp.actual_spent = total
