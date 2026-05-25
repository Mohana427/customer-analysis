from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
from datetime import datetime

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    plan_type = Column(String(50), default="basic", nullable=False)
    monthly_charges = Column(Float, default=9.99, nullable=False)
    contract_type = Column(String(20), default="monthly", nullable=False)
    subscription_start = Column(DateTime, default=datetime.utcnow, nullable=False)
    subscription_end = Column(DateTime, nullable=True)
    status = Column(String(20), default="active", index=True, nullable=False)
    churn_risk_score = Column(Float, default=0.0)
    last_login = Column(DateTime, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    login_events = relationship("LoginEvent", back_populates="customer", cascade="all, delete-orphan")
    support_tickets = relationship("SupportTicket", back_populates="customer", cascade="all, delete-orphan")
    churn_events = relationship("ChurnEvent", back_populates="customer", cascade="all, delete-orphan")
    risk_alerts = relationship("RiskAlert", back_populates="customer", cascade="all, delete-orphan")
    metrics = relationship("CustomerMetrics", back_populates="customer", uselist=False, cascade="all, delete-orphan")


class LoginEvent(Base):
    __tablename__ = "login_events"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), index=True, nullable=False)
    login_timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    session_duration_minutes = Column(Integer, default=0)
    pages_visited = Column(Integer, default=0)
    device_type = Column(String(20), default="web")
    feature_used = Column(String(100), nullable=True)

    customer = relationship("Customer", back_populates="login_events")


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), index=True, nullable=False)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), default="general", index=True, nullable=False)
    priority = Column(String(20), default="medium", nullable=False)
    sentiment_score = Column(Float, default=0.0)
    status = Column(String(20), default="open", index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    customer = relationship("Customer", back_populates="support_tickets")


class ChurnEvent(Base):
    __tablename__ = "churn_events"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), index=True, nullable=False)
    churn_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    churn_reason = Column(String(100), nullable=True)
    trigger_type = Column(String(50), index=True, nullable=False)
    days_since_last_login = Column(Integer, default=0)
    support_tickets_last_30_days = Column(Integer, default=0)
    risk_score_at_churn = Column(Float, default=0.0)
    contributing_factors = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    customer = relationship("Customer", back_populates="churn_events")


class RiskAlert(Base):
    __tablename__ = "risk_alerts"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), index=True, nullable=False)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), default="medium", index=True, nullable=False)
    message = Column(Text, nullable=False)
    is_acknowledged = Column(Boolean, default=False, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    customer = relationship("Customer", back_populates="risk_alerts")


class CustomerMetrics(Base):
    __tablename__ = "customer_metrics"

    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), primary_key=True)
    tenure_days = Column(Integer, default=0, nullable=False)
    total_logins_30d = Column(Integer, default=0, nullable=False)
    total_logins_90d = Column(Integer, default=0, nullable=False)
    avg_session_duration = Column(Float, default=0.0, nullable=False)
    days_since_last_login = Column(Integer, default=0, nullable=False)
    login_trend = Column(Float, default=0.0, nullable=False)
    total_support_tickets = Column(Integer, default=0, nullable=False)
    open_tickets = Column(Integer, default=0, nullable=False)
    avg_sentiment_score = Column(Float, default=0.0)
    last_computed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    customer = relationship("Customer", back_populates="metrics")
