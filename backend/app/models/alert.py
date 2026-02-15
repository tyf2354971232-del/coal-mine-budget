"""Alert log model."""
import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from app.database import Base


class AlertLog(Base):
    """System alert/warning log."""
    __tablename__ = "alert_logs"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), nullable=False)  # budget_overrun, schedule_delay, burn_rate, reserve_usage
    level = Column(String(20), nullable=False)  # info, yellow, red
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    related_type = Column(String(50), nullable=True)  # sub_project, cost_item, category
    related_id = Column(Integer, nullable=True)
    related_name = Column(String(200), nullable=True)
    is_read = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
