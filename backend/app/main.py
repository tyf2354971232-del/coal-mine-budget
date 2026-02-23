"""Main FastAPI application entry point."""
import traceback
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, async_session
from app.routers import auth, projects, budget, expenditures, dashboard, simulation, alerts, reports, cashflow, procurement
from app.services.seed_data import seed_initial_data

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    await init_db()
    async with async_session() as db:
        await seed_initial_data(db)
        await db.commit()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="煤矿技改项目概算管控与模拟分析系统 - 平煤神马塔能伊斯法拉公司",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API routers (must be registered BEFORE the static catch-all) ──
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(budget.router)
app.include_router(expenditures.router)
app.include_router(dashboard.router)
app.include_router(simulation.router)
app.include_router(alerts.router)
app.include_router(reports.router)
app.include_router(cashflow.router)
app.include_router(procurement.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    print(f"ERROR: {request.method} {request.url}\n{tb}")
    return JSONResponse(status_code=500, content={"detail": str(exc), "traceback": tb})


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


# ── Serve Vue SPA static files (only when built frontend exists) ──
if STATIC_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve Vue SPA — return index.html for all non-API, non-asset routes."""
        file = STATIC_DIR / full_path
        if file.is_file():
            return FileResponse(file)
        return FileResponse(STATIC_DIR / "index.html")
