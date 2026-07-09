"""
Vercel serverless entrypoint for Enterprise Digital COO.

Vercel runs Python as stateless serverless functions, so we create a
lightweight FastAPI app that wires up only the routes that work in a
stateless environment (metrics, reports, static HTML).

Features that require persistent infrastructure (PostgreSQL, WebSockets,
ChromaDB) are excluded here — use Railway or Render for the full stack.
"""
import sys
import os
import importlib.util
from pathlib import Path

# Make the backend package importable from this file's location
BACKEND_DIR = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import HTTPException, RequestValidationError

from config import settings


def _load_backend_module(module_name: str, relative_path: str):
    """Load backend modules without colliding with this top-level api package."""
    module_path = BACKEND_DIR / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


metrics = _load_backend_module("enterprise_coo_metrics", "api/v1/endpoints/metrics.py")
reports = _load_backend_module("enterprise_coo_reports", "api/v1/endpoints/reports.py")
notifications = _load_backend_module("enterprise_coo_notifications", "api/v1/endpoints/notifications.py")

# ── App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Enterprise Digital COO — Vercel deployment",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware ───────────────────────────────────────────────────────
# NOTE: GZipMiddleware is intentionally omitted — it can swallow HTTP exceptions
# and return plain-text "Internal Server Error" instead of JSON on Vercel.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global exception handlers — always return JSON ───────────────────
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {type(exc).__name__}: {exc}"},
    )

# ── Static files ─────────────────────────────────────────────────────
static_dir = Path(__file__).parent.parent / "backend" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# ── API routes ───────────────────────────────────────────────────────
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["metrics"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])


# ── Root & health ────────────────────────────────────────────────────
@app.get("/")
async def root():
    """Serve the main dashboard HTML."""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/googlecb411ad1aca4954f.html")
async def google_site_verification():
    """Serve Google Search Console ownership verification."""
    verification_file = static_dir / "googlecb411ad1aca4954f.html"
    return FileResponse(str(verification_file), media_type="text/html")


@app.get("/health")
async def health():
    return {"status": "healthy", "version": settings.APP_VERSION}
