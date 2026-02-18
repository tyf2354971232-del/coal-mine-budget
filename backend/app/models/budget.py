"""Budget category, cost item, and expenditure models."""
import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class BudgetCategory(Base):
    """Three-level budget category hierarchy."""
    __tablename__ = "budget_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), nullable=True, unique=True)  # 科目编码
    parent_id = Column(Integer, ForeignKey("budget_categories.id"), nullable=True)
    level = Column(Integer, default=1)  # 1=一级科目, 2=二级科目, 3=三级科目
    budget_amount = Column(Float, default=0)  # 概算金额 万元
    description = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0)

    parent = relationship("BudgetCategory", remote_side="BudgetCategory.id", backref="children")
    cost_items = relationship("CostItem", back_populates="category")


class CostItem(Base):
    """Specific cost item linking sub-project to budget category."""
    __tablename__ = "cost_items"

    id = Column(Integer, primary_key=True, index=True)
    sub_project_id = Column(Integer, ForeignKey("sub_projects.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("budget_categories.id"), nullable=True)
    name = Column(String(200), nullable=False)
    budget_amount = Column(Float, default=0)  # 概算金额 万元
    actual_amount = Column(Float, default=0)  # 实际金额 万元 (auto-calculated)
    unit = Column(String(50), nullable=True)
    quantity = Column(Float, nullable=True)
    unit_price = Column(Float, nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    sub_project = relationship("SubProject", back_populates="cost_items")
    category = relationship("BudgetCategory", back_populates="cost_items")
    expenditures = relationship("Expenditure", back_populates="cost_item", cascade="all, delete-orphan")


class Expenditure(Base):
    """Individual expenditure records."""
    __tablename__ = "expenditures"

    id = Column(Integer, primary_key=True, index=True)
    cost_item_id = Column(Integer, ForeignKey("cost_items.id"), nullable=True)
    sub_project_id = Column(Integer, ForeignKey("sub_projects.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("budget_categories.id"), nullable=True)
    record_date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)  # 万元
    description = Column(String(500), nullable=True)
    voucher_no = Column(String(100), nullable=True)  # 凭证号
    source = Column(String(50), default="manual")  # manual, excel_import, erp_sync
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    cost_item = relationship("CostItem", back_populates="expenditures")
    sub_project = relationship("SubProject", back_populates="expenditures")
