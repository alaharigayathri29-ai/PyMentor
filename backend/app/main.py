from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models.models import Base
from app.routers import auth, assessment, learning_path, mentor, practice, progress, admin, workspace
from app.seed_data import seed

# Create all DB tables
Base.metadata.create_all(bind=engine)

# Auto-migrate columns on startup
try:
    from app.migrate import migrate_database
    from app.config import settings
    if settings.DATABASE_URL.startswith("sqlite:///"):
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        migrate_database(db_path)
except Exception as e:
    print(f"[STARTUP] Migration warning: {e}")

# Auto-seed on first run (safe to call multiple times)
try:
    seed()
except Exception as e:
    print(f"[STARTUP] Seed warning: {e}")

app = FastAPI(
    title="AI Programming Mentor API",
    description="Full-stack API for the AI Programming Mentor platform.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

from app.config import settings

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        settings.FRONTEND_URL,
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|.*\.onrender\.com)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── No-Cache Middleware for Development & Fresh Asset Delivery ───────────────
@app.middleware("http")
async def add_cache_control_headers(request, call_next):
    response = await call_next(request)
    path = request.url.path
    if (
        path.endswith((".html", ".css", ".js", ".json"))
        or path == "/"
        or path.startswith("/api/")
    ):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(assessment.router)
app.include_router(learning_path.router)
app.include_router(mentor.router)
app.include_router(practice.router)
app.include_router(progress.router)
app.include_router(admin.router)
app.include_router(workspace.router)


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/api/health", tags=["health"])
@app.get("/health", tags=["health"])
def health():
    return {"status": "healthy"}


# ── Frontend Static Files Mount ──────────────────────────────────────────────
from fastapi.staticfiles import StaticFiles
from pathlib import Path


class NoCacheStaticFiles(StaticFiles):
    def file_response(self, *args, **kwargs):
        response = super().file_response(*args, **kwargs)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response


FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", NoCacheStaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
