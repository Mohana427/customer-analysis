# 🔍 The Leak Detector

**A full-stack data diagnostics system for identifying, analyzing, and preventing customer churn.**

The Leak Detector ingests user behavior data — tenure, login frequency, and support contacts — to isolate exact behavioral triggers causing subscription cancellations. It provides customer success teams with automated, actionable insights to boost user retention.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                    │
│  Dashboard  │  Customers  │  Analytics  │  Risk Alerts  │
└──────────────────────┬──────────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────────┐
│                   BACKEND (FastAPI)                       │
│  Event Ingestion │ Churn Engine │ ML Predictor │ Alerts  │
└──────────────────────┬──────────────────────────────────┘
                       │ SQLAlchemy ORM
┌──────────────────────▼──────────────────────────────────┐
│                  DATABASE (SQLite/PostgreSQL)             │
│  Customers │ Logins │ Tickets │ Churn Events │ Metrics  │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- **npm**

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python seed_data.py          # Generate synthetic data (500 customers)
python -m app.ml.train_model # Train the churn prediction model
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev                  # Starts on http://localhost:3000
```

### 3. Access the Dashboard
Open **http://localhost:3000** in your browser.

---

## 📊 Features

### Data Input Streams
| Stream | What It Tracks | Churn Signal |
|--------|---------------|-------------|
| **Tenure** | Customer lifespan & subscription duration | Short tenure = higher risk |
| **Login Frequency** | Daily/weekly engagement patterns | Declining logins = warning |
| **Support Contacts** | Ticket volume, frequency, sentiment | High negative sentiment = risk |

### Core Detection Rules
- **14-Day Inactivity Rule**: Flags users with zero logins for 14+ consecutive days
- **Feature Break Detection**: Correlates critical bug reports with cancellations within 7 days
- **ML Churn Prediction**: Random Forest model scores each customer 0.0–1.0 risk

### Dashboard Pages
1. **Overview**: KPI cards, churn rate trend, funnel segmentation, recent alerts
2. **Customers**: Searchable table with risk scores, status filters, activity timelines
3. **Analytics**: Tenure distribution, login heatmaps, cohort retention, feature importance
4. **Alerts**: Real-time risk alert feed with severity levels and acknowledgment

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Next.js 14, Recharts, Vanilla CSS | Analytics dashboard |
| Backend | FastAPI, SQLAlchemy, APScheduler | API & churn engine |
| Database | SQLite (dev) / PostgreSQL (prod) | Data storage |
| ML | scikit-learn, SHAP | Churn prediction & explainability |

---

## 📁 Project Structure

```
├── frontend/           # Next.js 14 dashboard
│   └── src/
│       ├── app/        # Pages (dashboard, customers, analytics, alerts)
│       ├── components/ # Reusable UI components
│       ├── hooks/      # Custom React hooks
│       └── lib/        # API client & utilities
│
├── backend/            # FastAPI backend
│   └── app/
│       ├── api/        # REST endpoints
│       ├── models/     # SQLAlchemy ORM models
│       ├── schemas/    # Pydantic validation schemas
│       ├── services/   # Business logic (churn detection)
│       ├── ml/         # ML pipeline (training & prediction)
│       └── tasks/      # Background scheduled tasks
│
└── database/           # SQL schema reference
```

## 📜 License

MIT
