"""Simulation models for what-if analysis and scenario comparison."""
import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Simulation(Base):
    """A simulation session that can contain multiple scenarios."""
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    sim_type = Column(String(50), nullable=False)  # whatif, scenario, sensitivity
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    scenarios = relationship("SimScenario", back_populates="simulation", cascade="all, delete-orphan")


class SimScenario(Base):
    """Individual scenario within a simulation."""
    __tablename__ = "sim_scenarios"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"), nullable=False)
    name = Column(String(200), nullable=False)  # e.g., "保守方案", "正常方案", "乐观方案"
    description = Column(Text, nullable=True)
    parameters = Column(JSON, nullable=True)  # Input parameters as JSON
    results = Column(JSON, nullable=True)  # Computed results as JSON
    total_cost = Column(Float, nullable=True)
    total_return = Column(Float, nullable=True)
    roi = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    simulation = relationship("Simulation", back_populates="scenarios")
