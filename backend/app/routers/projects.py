"""Projects and sub-projects router."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.models.project import Project, SubProject, MilestoneNode, ProgressRecord
from app.models.budget import Expenditure
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse,
    SubProjectCreate, SubProjectUpdate, SubProjectResponse,
    MilestoneCreate, MilestoneUpdate, MilestoneResponse,
    ProgressRecordCreate, ProgressRecordResponse,
)
from app.utils.security import get_current_user, require_role

router = APIRouter(prefix="/api/projects", tags=["工程项目管理"])


# ===== Project CRUD =====

@router.get("", response_model=list[ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """获取所有项目"""
    result = await db.execute(
        select(Project).options(selectinload(Project.sub_projects)).order_by(Project.id)
    )
    projects = result.scalars().all()
    responses = []
    for p in projects:
        pr = ProjectResponse.model_validate(p)
        pr.sub_projects = [await _enrich_sub_project(sp) for sp in p.sub_projects]
        responses.append(pr)
    return responses


@router.post("", response_model=ProjectResponse)
async def create_project(
    req: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "leader")),
):
    """创建项目"""
    project = Project(**req.model_dump())
    db.add(project)
    await db.flush()
    await db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """获取项目详情"""
    result = await db.execute(
        select(Project).options(selectinload(Project.sub_projects)).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    pr = ProjectResponse.model_validate(project)
    pr.sub_projects = [await _enrich_sub_project(sp) for sp in project.sub_projects]
    return pr


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    req: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "leader")),
):
    """更新项目"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    await db.flush()
    await db.refresh(project)
    return ProjectResponse.model_validate(project)


# ===== Sub-project CRUD =====

@router.get("/sub-projects/all", response_model=list[SubProjectResponse])
async def list_all_sub_projects(
    project_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取所有子工程（支持筛选）"""
    query = select(SubProject)
    if project_id:
        query = query.where(SubProject.project_id == project_id)
    if category:
        query = query.where(SubProject.category == category)
    if status:
        query = query.where(SubProject.status == status)
    query = query.order_by(SubProject.sort_order, SubProject.id)
    result = await db.execute(query)
    return [await _enrich_sub_project(sp) for sp in result.scalars().all()]


@router.post("/sub-projects", response_model=SubProjectResponse)
async def create_sub_project(
    req: SubProjectCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "leader", "department")),
):
    """创建子工程"""
    sp = SubProject(**req.model_dump())
    db.add(sp)
    await db.flush()
    await db.refresh(sp)
    return await _enrich_sub_project(sp)


@router.get("/sub-projects/{sp_id}", response_model=SubProjectResponse)
async def get_sub_project(sp_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """获取子工程详情"""
    result = await db.execute(select(SubProject).where(SubProject.id == sp_id))
    sp = result.scalar_one_or_none()
    if not sp:
        raise HTTPException(status_code=404, detail="子工程不存在")
    return await _enrich_sub_project(sp)


@router.put("/sub-projects/{sp_id}", response_model=SubProjectResponse)
async def update_sub_project(
    sp_id: int,
    req: SubProjectUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "leader", "department")),
):
    """更新子工程"""
    result = await db.execute(select(SubProject).where(SubProject.id == sp_id))
    sp = result.scalar_one_or_none()
    if not sp:
        raise HTTPException(status_code=404, detail="子工程不存在")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(sp, field, value)
    await db.flush()
    await db.refresh(sp)
    return await _enrich_sub_project(sp)


@router.delete("/sub-projects/{sp_id}")
async def delete_sub_project(
    sp_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    """删除子工程"""
    result = await db.execute(select(SubProject).where(SubProject.id == sp_id))
    sp = result.scalar_one_or_none()
    if not sp:
        raise HTTPException(status_code=404, detail="子工程不存在")
    await db.delete(sp)
    return {"message": "删除成功"}


# ===== Milestones =====

@router.get("/sub-projects/{sp_id}/milestones", response_model=list[MilestoneResponse])
async def list_milestones(sp_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(
        select(MilestoneNode).where(MilestoneNode.sub_project_id == sp_id).order_by(MilestoneNode.sort_order)
    )
    return [MilestoneResponse.model_validate(m) for m in result.scalars().all()]


@router.post("/milestones", response_model=MilestoneResponse)
async def create_milestone(
    req: MilestoneCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "leader", "department")),
):
    m = MilestoneNode(**req.model_dump())
    db.add(m)
    await db.flush()
    await db.refresh(m)
    return MilestoneResponse.model_validate(m)


@router.put("/milestones/{m_id}", response_model=MilestoneResponse)
async def update_milestone(
    m_id: int,
    req: MilestoneUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "leader", "department")),
):
    result = await db.execute(select(MilestoneNode).where(MilestoneNode.id == m_id))
    m = result.scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="里程碑不存在")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(m, field, value)
    await db.flush()
    await db.refresh(m)
    return MilestoneResponse.model_validate(m)


# ===== Progress Records =====

@router.get("/sub-projects/{sp_id}/progress", response_model=list[ProgressRecordResponse])
async def list_progress(sp_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(
        select(ProgressRecord).where(ProgressRecord.sub_project_id == sp_id).order_by(ProgressRecord.record_date.desc())
    )
    return [ProgressRecordResponse.model_validate(p) for p in result.scalars().all()]


@router.post("/progress", response_model=ProgressRecordResponse)
async def create_progress_record(
    req: ProgressRecordCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "leader", "department")),
):
    """记录进度（同时更新子工程进度百分比）"""
    pr = ProgressRecord(**req.model_dump(), created_by=user.id)
    db.add(pr)
    # Update sub-project progress
    result = await db.execute(select(SubProject).where(SubProject.id == req.sub_project_id))
    sp = result.scalar_one_or_none()
    if sp:
        sp.progress_percent = req.percent
        if req.percent > 0 and sp.status == "not_started":
            sp.status = "in_progress"
        if req.percent >= 100:
            sp.status = "completed"
    await db.flush()
    await db.refresh(pr)
    return ProgressRecordResponse.model_validate(pr)


# ===== Helpers =====

async def _enrich_sub_project(sp: SubProject) -> SubProjectResponse:
    """Add computed fields to sub-project response."""
    resp = SubProjectResponse.model_validate(sp)
    if sp.allocated_budget and sp.allocated_budget > 0:
        resp.budget_usage_rate = round(sp.actual_spent / sp.allocated_budget * 100, 2)
        resp.is_over_budget = sp.actual_spent > sp.allocated_budget
    return resp
