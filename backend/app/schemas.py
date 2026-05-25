from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

class CustomerBase(BaseModel):
    email: str
    name: str
    plan_type: str = "basic"
    monthly_charges: float = 9.99
    contract_type: str = "monthly"

class CustomerCreate(CustomerBase):
    pass

class CustomerMetricsSchema(BaseModel):
    tenure_days: int
    total_logins_30d: int
    total_logins_90d: int
    avg_session_duration: float
    days_since_last_login: int
    login_trend: float
    total_support_tickets: int
    open_tickets: int
    avg_sentiment_score: float

    model_config = ConfigDict(from_attributes=True)

class CustomerResponse(CustomerBase):
    id: int
    status: str
    churn_risk_score: float
    subscription_start: datetime
    subscription_end: Optional[datetime] = None
    last_login: Optional[datetime] = None
    metrics: Optional[CustomerMetricsSchema] = None

    model_config = ConfigDict(from_attributes=True)

class LoginEventCreate(BaseModel):
    customer_id: int
    session_duration_minutes: int = 0
    pages_visited: int = 0
    device_type: str = "web"
    feature_used: Optional[str] = None

class SupportTicketCreate(BaseModel):
    customer_id: int
    subject: str
    description: Optional[str] = None
    category: str = "general"
    priority: str = "medium"

class RiskAlertResponse(BaseModel):
    id: int
    customer_id: int
    alert_type: str
    severity: str
    message: str
    is_acknowledged: bool
    created_at: datetime
    customer: Optional[CustomerResponse] = None

    model_config = ConfigDict(from_attributes=True)

class DashboardAnalytics(BaseModel):
    total_active: int
    churn_rate: float
    at_risk_count: int
    avg_lifetime_days: float
