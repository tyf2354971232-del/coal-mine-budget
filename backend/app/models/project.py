"""Project and sub-project models."""
import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Project(Base):
    """Main project entity - the overall technical renovation project."""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    total_budget = Column(Float, nullable=False)  # 万元
    reserve_rate = Column(Float, default=0.07)  # 弹性预备金比例 5%-10%
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    status = Column(String(20), default="planning")  # planning, in_progress, completed, suspended
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    sub_projects = relationship("SubProject", back_populates="project", cascade="all, delete-orphan")


class SubProject(Base):
    """Sub-project / work item under the main project."""
    __tablename__ = "sub_projects"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)  # 矿建工程费, 土建工程费, 安装工程费, 设备购置费, 其他费用, 预备费
    allocated_budget = Column(Float, default=0)  # 万元
    actual_spent = Column(Float, default=0)  # 万元 (auto-calculated)
    progress_percent = Column(Float, default=0)  # 0-100
    status = Column(String(20), default="not_started")  # not_started, in_progress, completed, delayed, suspended
    planned_start = Column(Date, nullable=True)
    planned_end = Column(Date, nullable=True)
    actual_start = Column(Date, nullable=True)
    actual_end = Column(Date, nullable=True)
    responsible_dept = Column(String(100), nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="sub_projects")
    milestones = relationship("MilestoneNode", back_populates="sub_project", cascade="all, delete-orphan")
    progress_records = relationship("ProgressRecord", back_populates="sub_project", cascade="all, delete-orphan")
    cost_items = relationship("CostItem", back_populates="sub_project", cascade="all, delete-orphan")
    expenditures = relationship("Expenditure", back_populates="sub_project", cascade="all, delete-orphan")


class MilestoneNode(Base):
    """Milestone nodes for sub-projects."""
    __tablename__ = "milestone_nodes"

    id = Column(Integer, primary_key=True, index=True)
    sub_project_id = Column(Integer, ForeignKey("sub_projects.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    planned_date = Column(Date, nullable=True)
    actual_date = Column(Date, nullable=True)
    status = Column(String(20), default="pending")  # pending, completed, delayed
    sort_order = Column(Integer, default=0)

    sub_project = relationship("SubProject", back_populates="milestones")


class ProgressRecord(Base):
    """Monthly progress records for sub-projects."""
    __tablename__ = "progress_records"

    id = Column(Integer, primary_key=True, index=True)
    sub_project_id = Column(Integer, ForeignKey("sub_projects.id"), nullable=False)
    record_date = Column(Date, nullable=False)
    percent = Column(Float, nullable=False)  # 0-100
    milestone = Column(String(200), nullable=True)
    note = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    sub_project = relationship("SubProject", back_populates="progress_records")
