import asyncio
import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from xgboost import XGBClassifier
import joblib
import os

from app.db.session import SessionLocal
from app.models import Customer, CustomerMetrics

async def fetch_training_data():
    async with SessionLocal() as db:
        # Join Customer and CustomerMetrics
        stmt = select(Customer, CustomerMetrics).join(CustomerMetrics, Customer.id == CustomerMetrics.customer_id)
        result = await db.execute(stmt)
        
        data = []
        for customer, metrics in result.all():
            data.append({
                'customer_id': customer.id,
                'tenure_days': metrics.tenure_days,
                'total_logins_30d': metrics.total_logins_30d,
                'total_logins_90d': metrics.total_logins_90d,
                'days_since_last_login': metrics.days_since_last_login,
                'avg_session_duration': metrics.avg_session_duration,
                'login_trend': metrics.login_trend,
                'total_support_tickets': metrics.total_support_tickets,
                'open_tickets': metrics.open_tickets,
                'avg_sentiment_score': metrics.avg_sentiment_score,
                'monthly_charges': customer.monthly_charges,
                'contract_type': customer.contract_type,
                'plan_type': customer.plan_type,
                # Target variable: 1 if churned, 0 otherwise
                'is_churned': 1 if customer.status == 'churned' else 0
            })
            
        return pd.DataFrame(data)

def train_model():
    print("Fetching training data from database...")
    df = asyncio.run(fetch_training_data())
    
    if df.empty:
        print("No training data found. Please run seed_data.py first.")
        return

    print(f"Loaded {len(df)} records.")
    
    # Separate features and target
    X = df.drop(columns=['customer_id', 'is_churned'])
    y = df['is_churned']
    
    # Calculate scale_pos_weight for XGBoost to handle imbalanced data
    # (number of negative samples / number of positive samples)
    neg_cases = (y == 0).sum()
    pos_cases = (y == 1).sum()
    scale_weight = neg_cases / pos_cases if pos_cases > 0 else 1.0
    
    # Define features
    numeric_features = [
        'tenure_days', 'total_logins_30d', 'total_logins_90d',
        'days_since_last_login', 'avg_session_duration', 'login_trend',
        'total_support_tickets', 'open_tickets', 'avg_sentiment_score',
        'monthly_charges'
    ]
    categorical_features = ['contract_type', 'plan_type']
    
    # Preprocessing pipeline
    preprocessor = ColumnTransformer(transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), categorical_features),
    ])
    
    # Full pipeline with XGBoost
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            scale_pos_weight=scale_weight,
            eval_metric='aucpr',
            random_state=42
        ))
    ])
    
    print("Training XGBoost model...")
    pipeline.fit(X, y)
    
    # Evaluate briefly on training data (in real life, do cross-validation)
    from sklearn.metrics import average_precision_score, classification_report
    y_pred = pipeline.predict(X)
    y_prob = pipeline.predict_proba(X)[:, 1]
    
    print("\nTraining set performance:")
    print(classification_report(y, y_pred))
    print(f"PR-AUC: {average_precision_score(y, y_prob):.4f}")
    
    # Save the model
    os.makedirs('ml_models', exist_ok=True)
    model_path = 'ml_models/churn_model_v1.joblib'
    joblib.dump(pipeline, model_path)
    print(f"\nModel saved to {model_path}")

if __name__ == "__main__":
    train_model()
