"""Main FastAPI application entry point."""
import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, async_session
from app.routers import auth, projects, budget, expenditures, dashboard, simulation, alerts, reports, cashflow
from app.services.seed_data import seed_initial_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    # Startup
    await init_db()
    async with async_session() as db:
        await seed_initial_data(db)
        await db.commit()
    yield
    # Shutdown (cleanup if needed)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="煤矿技改项目概算管控与模拟分析系统 - 平煤神马塔能伊斯法拉公司",
    lifespan=lifespan,
)

# CORS middleware (configurable via CORS_ORIGINS env var)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(budget.router)
app.include_router(expenditures.router)
app.include_router(dashboard.router)
app.include_router(simulation.router)
app.include_router(alerts.router)
app.include_router(reports.router)
app.include_router(cashflow.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    print(f"ERROR: {request.method} {request.url}\n{tb}")
    return JSONResponse(status_code=500, content={"detail": str(exc), "traceback": tb})


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
