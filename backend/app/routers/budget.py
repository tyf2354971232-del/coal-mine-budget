"""Budget categories and cost items router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.budget import BudgetCategory, CostItem, Expenditure
from app.schemas.budget import (
    BudgetCategoryCreate, BudgetCategoryUpdate, BudgetCategoryResponse,
    CostItemCreate, CostItemUpdate, CostItemResponse,
)
from app.utils.security import get_current_user, require_role

router = APIRouter(prefix="/api/budget", tags=["预算科目管理"])


# ===== Budget Categories =====

@router.get("/categories", response_model=list[BudgetCategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """获取预算科目列表（树形结构）"""
    result = await db.execute(select(BudgetCategory).order_by(BudgetCategory.level, BudgetCategory.sort_order))
    categories = result.scalars().all()

    # Calculate actual spent for each category
    cat_list = []
    for cat in categories:
        exp_result = await db.execute(
            select(func.coalesce(func.sum(Expenditure.amount), 0))
            .where(Expenditure.category_id == cat.id)
        )
        actual_spent = float(exp_result.scalar())
        cr = BudgetCategoryResponse(
            id=cat.id, name=cat.name, code=cat.code, parent_id=cat.parent_id,
            level=cat.level, budget_amount=cat.budget_amount,
            description=cat.description, sort_order=cat.sort_order,
            actual_spent=actual_spent, children=[],
        )
        cat_list.append(cr)

    # Build tree structure
    return _build_tree(cat_list)


@router.get("/categories/flat", response_model=list[BudgetCategoryResponse])
async def list_categories_flat(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """获取预算科目平铺列表"""
    result = await db.execute(select(BudgetCategory).order_by(BudgetCategory.level, BudgetCategory.sort_order))
    categories = result.scalars().all()
    cat_list = []
    for cat in categories:
        exp_result = await db.execute(
            select(func.coalesce(func.sum(Expenditure.amount), 0))
            .where(Expenditure.category_id == cat.id)
        )
        actual_spent = float(exp_result.scalar())
        cr = BudgetCategoryResponse(
            id=cat.id, name=cat.name, code=cat.code, parent_id=cat.parent_id,
            level=cat.level, budget_amount=cat.budget_amount,
            description=cat.description, sort_order=cat.sort_order,
            actual_spent=actual_spent, children=[],
        )
        cat_list.append(cr)
    return cat_list


@router.post("/categories", response_model=BudgetCategoryResponse)
async def create_category(
    req: BudgetCategoryCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "leader")),
):
    """创建预算科目"""
    cat = BudgetCategory(**req.model_dump())
    db.add(cat)
    await db.flush()
    await db.refresh(cat)
    return BudgetCategoryResponse.model_validate(cat)


@router.put("/categories/{cat_id}", response_model=BudgetCategoryResponse)
async def update_category(
    cat_id: int,
    req: BudgetCategoryUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "leader")),
):
    """更新预算科目"""
    result = await db.execute(select(BudgetCategory).where(BudgetCategory.id == cat_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="科目不存在")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(cat, field, value)
    await db.flush()
    await db.refresh(cat)
    return BudgetCategoryResponse.model_validate(cat)


@router.delete("/categories/{cat_id}")
async def delete_category(
    cat_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    result = await db.execute(select(BudgetCategory).where(BudgetCategory.id == cat_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="科目不存在")
    await db.delete(cat)
    return {"message": "删除成功"}


# ===== Cost Items =====

@router.get("/cost-items", response_model=list[CostItemResponse])
async def list_cost_items(
    sub_project_id: int = None,
    category_id: int = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取成本项列表"""
    query = select(CostItem)
    if sub_project_id:
        query = query.where(CostItem.sub_project_id == sub_project_id)
    if category_id:
        query = query.where(CostItem.category_id == category_id)
    result = await db.execute(query.order_by(CostItem.id))
    items = []
    for ci in result.scalars().all():
        cir = CostItemResponse.model_validate(ci)
        if ci.budget_amount and ci.budget_amount > 0:
            cir.usage_rate = round(ci.actual_amount / ci.budget_amount * 100, 2)
        items.append(cir)
    return items


@router.post("/cost-items", response_model=CostItemResponse)
async def create_cost_item(
    req: CostItemCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "leader", "department")),
):
    ci = CostItem(**req.model_dump())
    db.add(ci)
    await db.flush()
    await db.refresh(ci)
    return CostItemResponse.model_validate(ci)


@router.put("/cost-items/{ci_id}", response_model=CostItemResponse)
async def update_cost_item(
    ci_id: int,
    req: CostItemUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "leader", "department")),
):
    result = await db.execute(select(CostItem).where(CostItem.id == ci_id))
    ci = result.scalar_one_or_none()
    if not ci:
        raise HTTPException(status_code=404, detail="成本项不存在")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(ci, field, value)
    await db.flush()
    await db.refresh(ci)
    return CostItemResponse.model_validate(ci)


@router.delete("/cost-items/{ci_id}")
async def delete_cost_item(
    ci_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    result = await db.execute(select(CostItem).where(CostItem.id == ci_id))
    ci = result.scalar_one_or_none()
    if not ci:
        raise HTTPException(status_code=404, detail="成本项不存在")
    await db.delete(ci)
    return {"message": "删除成功"}


def _build_tree(categories: list[BudgetCategoryResponse]) -> list[BudgetCategoryResponse]:
    """Build tree from flat category list."""
    cat_map = {c.id: c for c in categories}
    roots = []
    for c in categories:
        if c.parent_id and c.parent_id in cat_map:
            cat_map[c.parent_id].children.append(c)
        else:
            roots.append(c)
    return roots
