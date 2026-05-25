-- =============================================================================
-- The Leak Detector — Database Schema
-- Full-stack churn detection and prevention system
-- =============================================================================

-- 1. Customers: subscription profiles and tenure tracking
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    plan_type VARCHAR(50) NOT NULL DEFAULT 'basic',       -- 'basic', 'pro', 'enterprise'
    monthly_charges DECIMAL(10, 2) NOT NULL DEFAULT 9.99,
    contract_type VARCHAR(20) NOT NULL DEFAULT 'monthly',  -- 'monthly', 'annual', 'two_year'
    subscription_start TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    subscription_end TIMESTAMP NULL,                       -- NULL = active subscriber
    status VARCHAR(20) NOT NULL DEFAULT 'active',          -- 'active', 'at_risk', 'churned'
    churn_risk_score FLOAT DEFAULT 0.0,                    -- 0.0 - 1.0 from ML model
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(status);
CREATE INDEX IF NOT EXISTS idx_customers_last_login ON customers(last_login);
CREATE INDEX IF NOT EXISTS idx_customers_plan ON customers(plan_type);

-- 2. Login Events: user engagement and session tracking
CREATE TABLE IF NOT EXISTS login_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    login_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    session_duration_minutes INTEGER DEFAULT 0,
    pages_visited INTEGER DEFAULT 0,
    device_type VARCHAR(20) DEFAULT 'web',                 -- 'web', 'mobile', 'api'
    feature_used VARCHAR(100) NULL
);

CREATE INDEX IF NOT EXISTS idx_login_customer ON login_events(customer_id);
CREATE INDEX IF NOT EXISTS idx_login_timestamp ON login_events(login_timestamp);

-- 3. Support Tickets: customer service interaction tracking
CREATE TABLE IF NOT EXISTS support_tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    subject VARCHAR(255) NOT NULL,
    description TEXT NULL,
    category VARCHAR(50) NOT NULL DEFAULT 'general',       -- 'bug', 'billing', 'feature_request', 'complaint', 'general'
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',        -- 'low', 'medium', 'high', 'critical'
    sentiment_score FLOAT DEFAULT 0.0,                     -- -1.0 to 1.0
    status VARCHAR(20) NOT NULL DEFAULT 'open',            -- 'open', 'in_progress', 'resolved', 'closed'
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL
);

CREATE INDEX IF NOT EXISTS idx_tickets_customer ON support_tickets(customer_id);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON support_tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_category ON support_tickets(category);

-- 4. Churn Events: historical cancellation records for analysis
CREATE TABLE IF NOT EXISTS churn_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    churn_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    churn_reason VARCHAR(100) NULL,                        -- 'inactivity', 'feature_break', 'pricing', 'competitor', 'other'
    trigger_type VARCHAR(50) NOT NULL,                     -- '14_day_inactivity', 'feature_break', 'manual', 'model_predicted'
    days_since_last_login INTEGER DEFAULT 0,
    support_tickets_last_30_days INTEGER DEFAULT 0,
    risk_score_at_churn FLOAT DEFAULT 0.0,
    contributing_factors TEXT NULL,                         -- JSON string of SHAP values
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_churn_customer ON churn_events(customer_id);
CREATE INDEX IF NOT EXISTS idx_churn_trigger ON churn_events(trigger_type);

-- 5. Risk Alerts: automated warnings for customer success teams
CREATE TABLE IF NOT EXISTS risk_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL,                       -- 'inactivity_warning', 'high_churn_risk', 'feature_break', 'sentiment_drop'
    severity VARCHAR(20) NOT NULL DEFAULT 'medium',        -- 'low', 'medium', 'high', 'critical'
    message TEXT NOT NULL,
    is_acknowledged BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_alerts_customer ON risk_alerts(customer_id);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON risk_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged ON risk_alerts(is_acknowledged);

-- 6. Customer Metrics: denormalized pre-computed metrics for fast queries + ML features
CREATE TABLE IF NOT EXISTS customer_metrics (
    customer_id INTEGER PRIMARY KEY REFERENCES customers(id) ON DELETE CASCADE,
    tenure_days INTEGER NOT NULL DEFAULT 0,
    total_logins_30d INTEGER NOT NULL DEFAULT 0,
    total_logins_90d INTEGER NOT NULL DEFAULT 0,
    avg_session_duration FLOAT NOT NULL DEFAULT 0.0,
    days_since_last_login INTEGER NOT NULL DEFAULT 0,
    login_trend FLOAT NOT NULL DEFAULT 0.0,                -- logins_30d / logins_90d ratio
    total_support_tickets INTEGER NOT NULL DEFAULT 0,
    open_tickets INTEGER NOT NULL DEFAULT 0,
    avg_sentiment_score FLOAT DEFAULT 0.0,
    last_computed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
