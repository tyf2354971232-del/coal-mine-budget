"""Cash flow management model."""
import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class CashFlow(Base):
    """Cash flow record - tracks money in (拨款) and out (支出)."""
    __tablename__ = "cash_flows"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    flow_type = Column(String(20), nullable=False)  # outflow / inflow
    category = Column(String(100), nullable=True)
    amount = Column(Float, nullable=False)  # 万元
    record_date = Column(Date, nullable=False)
    payee = Column(String(200), nullable=True)
    payment_method = Column(String(50), nullable=True)  # 银行转账/现金/支票
    description = Column(String(500), nullable=True)
    voucher_no = Column(String(100), nullable=True)
    related_sub_project_id = Column(Integer, ForeignKey("sub_projects.id"), nullable=True)
    status = Column(String(20), default="paid")  # pending/approved/paid/cancelled
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project")
    related_sub_project = relationship("SubProject")
