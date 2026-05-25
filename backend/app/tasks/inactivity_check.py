import logging
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.models import Customer, RiskAlert, ChurnEvent
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)

async def check_inactive_users():
    """Background task to find users inactive for 14+ days and flag them."""
    logger.info("Running 14-day inactivity check...")
    
    async with SessionLocal() as db:
        cutoff_date = datetime.utcnow() - timedelta(days=14)
        
        # Find active customers whose last login is before cutoff
        stmt = select(Customer).where(
            Customer.status == "active",
            Customer.last_login < cutoff_date
        )
        
        result = await db.execute(stmt)
        inactive_customers = result.scalars().all()
        
        for customer in inactive_customers:
            # 1. Update status
            customer.status = "at_risk"
            customer.churn_risk_score = 0.9  # High risk due to inactivity
            
            # 2. Create Risk Alert
            alert = RiskAlert(
                customer_id=customer.id,
                alert_type="inactivity_warning",
                severity="high",
                message=f"Customer has not logged in since {customer.last_login.strftime('%Y-%m-%d')}. High risk of silent churn."
            )
            db.add(alert)
            
            # 3. Log potential churn trigger event for tracking
            churn_event = ChurnEvent(
                customer_id=customer.id,
                trigger_type="14_day_inactivity",
                days_since_last_login=(datetime.utcnow() - customer.last_login).days,
                risk_score_at_churn=0.9
            )
            db.add(churn_event)
            
        await db.commit()
        logger.info(f"Flagged {len(inactive_customers)} inactive users.")
