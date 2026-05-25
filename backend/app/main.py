from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
from app.core.config import settings
from app.services.ml_predictor import predictor
from app.tasks.inactivity_check import check_inactive_users
from app.api.endpoints import router as api_router
from app.db.session import engine, Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Create database tables (in dev, usually use Alembic in prod)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # 2. Load ML model
    predictor.load_model(settings.MODEL_PATH)
    
    # 3. Start Background Scheduler
    scheduler = AsyncIOScheduler()
    # In production, check daily. For demo/dev, every minute or hour is fine.
    scheduler.add_job(check_inactive_users, "interval", hours=24)
    scheduler.start()
    logger.info("Background scheduler started.")
    
    yield
    
    # Shutdown
    scheduler.shutdown()
    logger.info("Background scheduler shut down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Welcome to The Leak Detector API"}
