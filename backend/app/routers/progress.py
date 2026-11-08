from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.routers.auth import get_current_user
from app.services import progress_service

router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.get("/")
def get_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Full progress summary for the logged-in student."""
    return progress_service.get_progress_summary(db, current_user.id)


@router.get("/leaderboard")
def get_leaderboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Platform leaderboard ranking students by XP and problems solved."""
    return progress_service.get_leaderboard(db, limit=10)

