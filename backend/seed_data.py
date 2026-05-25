import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import engine, Base, SessionLocal
from app.models import Customer, LoginEvent, SupportTicket, ChurnEvent, RiskAlert, CustomerMetrics

async def clear_db(db: AsyncSession):
    # For SQLite, it's easier to drop all and recreate
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

async def generate_seed_data():
    async with SessionLocal() as db:
        await clear_db(db)
        
        print("Generating 500 customers...")
        customers = []
        now = datetime.utcnow()
        
        # 1. Create Customers
        for i in range(1, 501):
            # Randomize tenure (1 to 1000 days)
            tenure_days = random.randint(1, 1000)
            start_date = now - timedelta(days=tenure_days)
            
            # 25% churn rate, 15% at risk, 60% active
            rand_status = random.random()
            if rand_status < 0.25:
                status = "churned"
                end_date = start_date + timedelta(days=random.randint(1, tenure_days))
                last_login = end_date - timedelta(days=random.randint(1, 30))
            elif rand_status < 0.40:
                status = "at_risk"
                end_date = None
                last_login = now - timedelta(days=random.randint(10, 25)) # Inactive
            else:
                status = "active"
                end_date = None
                last_login = now - timedelta(days=random.randint(0, 5))
                
            plan = random.choice(["basic", "pro", "enterprise"])
            charges = {"basic": 9.99, "pro": 29.99, "enterprise": 99.99}[plan]
            
            customer = Customer(
                email=f"user{i}@example.com",
                name=f"Customer {i}",
                plan_type=plan,
                monthly_charges=charges,
                contract_type=random.choice(["monthly", "annual"]),
                subscription_start=start_date,
                subscription_end=end_date,
                status=status,
                last_login=last_login,
                churn_risk_score=random.uniform(0.7, 1.0) if status in ["churned", "at_risk"] else random.uniform(0.0, 0.3)
            )
            db.add(customer)
            customers.append(customer)
            
        await db.commit()
        
        print("Generating login events, tickets, and metrics...")
        # Get all customers with their IDs assigned
        result = await db.execute(Customer.__table__.select())
        saved_customers = result.all()
        
        for c in saved_customers:
            cid = c.id
            is_churned = c.status == "churned"
            
            # Metrics
            total_logins = random.randint(1, 10) if is_churned else random.randint(20, 100)
            total_tickets = random.randint(3, 10) if is_churned else random.randint(0, 2)
            avg_sentiment = random.uniform(-1.0, 0.0) if is_churned else random.uniform(0.0, 1.0)
            
            # Create a metrics record directly to save time computing it
            metrics = CustomerMetrics(
                customer_id=cid,
                tenure_days=(now - c.subscription_start).days,
                total_logins_30d=total_logins,
                total_logins_90d=total_logins * 3,
                avg_session_duration=random.uniform(1.0, 30.0),
                days_since_last_login=(now - c.last_login).days if c.last_login else 0,
                login_trend=random.uniform(0.1, 0.5) if is_churned else random.uniform(0.8, 1.2),
                total_support_tickets=total_tickets,
                open_tickets=1 if is_churned else 0,
                avg_sentiment_score=avg_sentiment
            )
            db.add(metrics)
            
            if is_churned:
                # Add churn event
                churn = ChurnEvent(
                    customer_id=cid,
                    churn_date=c.subscription_end,
                    churn_reason=random.choice(["pricing", "competitor", "feature_break", "inactivity"]),
                    trigger_type="model_predicted",
                    days_since_last_login=15,
                    risk_score_at_churn=0.85
                )
                db.add(churn)
                
            if c.status == "at_risk":
                alert = RiskAlert(
                    customer_id=cid,
                    alert_type="inactivity_warning" if random.random() > 0.5 else "feature_break",
                    severity="high",
                    message="High churn risk detected based on recent behavior."
                )
                db.add(alert)
                
        await db.commit()
        print("Seed data generation complete!")

if __name__ == "__main__":
    asyncio.run(generate_seed_data())
