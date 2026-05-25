from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List
from app.db.session import get_db
from app.models import Customer, LoginEvent, SupportTicket, RiskAlert, ChurnEvent
from app.schemas import (
    CustomerResponse, CustomerCreate, LoginEventCreate, 
    SupportTicketCreate, RiskAlertResponse, DashboardAnalytics
)
from datetime import datetime

router = APIRouter()

# --- Customers ---

@router.get("/customers", response_model=List[CustomerResponse])
async def list_customers(skip: int = 0, limit: int = 100, status: str = None, db: AsyncSession = Depends(get_db)):
    stmt = select(Customer).options(selectinload(Customer.metrics))
    if status:
        stmt = stmt.where(Customer.status == status)
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Customer).options(selectinload(Customer.metrics)).where(Customer.id == customer_id)
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

# --- Events (Ingestion) ---

@router.post("/events/login")
async def log_login(event: LoginEventCreate, db: AsyncSession = Depends(get_db)):
    # 1. Add event
    db_event = LoginEvent(**event.model_dump())
    db.add(db_event)
    
    # 2. Update customer last_login
    stmt = select(Customer).where(Customer.id == event.customer_id)
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()
    if customer:
        customer.last_login = datetime.utcnow()
        if customer.status == "at_risk":
            # Potential win-back or normal activity resumption
            # Real logic would re-evaluate risk score here
            pass
            
    await db.commit()
    return {"status": "success"}

@router.post("/events/support-ticket")
async def create_ticket(ticket: SupportTicketCreate, db: AsyncSession = Depends(get_db)):
    db_ticket = SupportTicket(**ticket.model_dump())
    db.add(db_ticket)
    
    # Simple feature break detection logic hook
    if ticket.category == "bug" and ticket.priority in ["high", "critical"]:
        alert = RiskAlert(
            customer_id=ticket.customer_id,
            alert_type="feature_break",
            severity="high",
            message=f"Critical bug reported: {ticket.subject}. High churn risk."
        )
        db.add(alert)
        
    await db.commit()
    return {"status": "success", "ticket_id": db_ticket.id}

# --- Analytics Dashboard ---

@router.get("/analytics/overview", response_model=DashboardAnalytics)
async def get_analytics_overview(db: AsyncSession = Depends(get_db)):
    # Total Active
    active_result = await db.execute(select(func.count(Customer.id)).where(Customer.status == "active"))
    total_active = active_result.scalar() or 0
    
    # Total Churned
    churn_result = await db.execute(select(func.count(Customer.id)).where(Customer.status == "churned"))
    total_churned = churn_result.scalar() or 0
    
    # At Risk
    risk_result = await db.execute(select(func.count(Customer.id)).where(Customer.status == "at_risk"))
    at_risk_count = risk_result.scalar() or 0
    
    # Churn Rate calculation
    total_customers = total_active + total_churned + at_risk_count
    churn_rate = (total_churned / total_customers * 100) if total_customers > 0 else 0.0
    
    # Avg Lifetime (simplified as avg days since start for all)
    # Note: In real app, calculate actual tenure for churned users
    
    return DashboardAnalytics(
        total_active=total_active,
        churn_rate=round(churn_rate, 2),
        at_risk_count=at_risk_count,
        avg_lifetime_days=120.5  # placeholder, would compute from metrics table
    )

# --- Alerts ---

@router.get("/alerts", response_model=List[RiskAlertResponse])
async def list_alerts(unacknowledged_only: bool = True, db: AsyncSession = Depends(get_db)):
    stmt = select(RiskAlert)
    if unacknowledged_only:
        stmt = stmt.where(RiskAlert.is_acknowledged == False)
    stmt = stmt.order_by(RiskAlert.created_at.desc()).limit(50)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.put("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(RiskAlert).where(RiskAlert.id == alert_id)
    result = await db.execute(stmt)
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert.is_acknowledged = True
    await db.commit()
    return {"status": "acknowledged"}
