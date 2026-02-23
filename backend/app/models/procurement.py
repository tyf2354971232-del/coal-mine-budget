"""Procurement, warehouse outbound, and civil settlement models."""
import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Text
from app.database import Base


class CivilSettlement(Base):
    """土建工程决算 - 按审核金额的80%开票入账。"""
    __tablename__ = "civil_settlements"

    id = Column(Integer, primary_key=True, index=True)
    seq = Column(Integer, nullable=False)
    project_name = Column(String(200), nullable=False)
    audit_amount = Column(Float, nullable=True)  # 审核金额(元)
    settlement_amount = Column(Float, nullable=False)  # 按80%入账金额(元)
    payment_plan = Column(Float, nullable=True)  # 拟付款计划(元), 施工方汇总
    somoni_amount = Column(Float, nullable=True)  # 索莫尼
    somoni_40_percent = Column(Float, nullable=True)  # 拟支付40%额度(索莫尼)
    feb_plan_somoni = Column(Float, nullable=True)  # 2月份计划支付(索莫尼)
    debt_somoni = Column(Float, nullable=True)  # 欠款(索莫尼)
    contractor = Column(String(100), nullable=True)  # 施工单位
    sub_project_id = Column(Integer, ForeignKey("sub_projects.id"), nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ProcurementMonthlySummary(Base):
    """塔国采购月度汇总。"""
    __tablename__ = "procurement_monthly_summaries"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(Integer, nullable=False)  # 1-12
    amount_somoni = Column(Float, default=0)  # 塔币索莫尼
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ProcurementRecord(Base):
    """塔国采购明细记录。"""
    __tablename__ = "procurement_records"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(Integer, nullable=False)  # 1-12
    seq = Column(Integer, nullable=True)
    material_name = Column(String(300), nullable=False)
    specification = Column(String(300), nullable=True)
    unit = Column(String(50), nullable=True)
    plan_price = Column(Float, nullable=True)
    plan_quantity = Column(Float, nullable=True)
    purchase_unit_price_somoni = Column(Float, nullable=True)
    purchase_method = Column(String(50), nullable=True)
    payment_method = Column(String(50), nullable=True)
    purchase_quantity = Column(Float, nullable=True)
    purchase_amount_somoni = Column(Float, nullable=True)
    stock_quantity = Column(Float, nullable=True)
    unit_price_rmb = Column(Float, nullable=True)
    amount_rmb = Column(Float, nullable=True)  # 人民币元
    usage_unit = Column(String(50), nullable=True)
    project_name = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class WarehouseOutbound(Base):
    """来塔物资出库明细记录。"""
    __tablename__ = "warehouse_outbound"

    id = Column(Integer, primary_key=True, index=True)
    team = Column(String(100), nullable=True)  # 使用区队
    apply_date = Column(Date, nullable=True)  # 申请日期
    material_type = Column(String(50), nullable=True)  # 物料类型
    material_code = Column(String(100), nullable=True)  # 物料编码
    material_name = Column(String(300), nullable=False)  # 物料名称
    specification = Column(String(300), nullable=True)  # 规格型号
    unit = Column(String(50), nullable=True)
    quantity = Column(Float, nullable=True)  # 出库数量
    unit_price = Column(Float, nullable=True)  # 单价（人民币元）
    amount = Column(Float, nullable=True)  # 金额（人民币元）
    usage_unit = Column(String(50), nullable=True)
    project_name = Column(String(200), nullable=True)  # 工程名称
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
