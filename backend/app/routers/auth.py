from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.models.models import User
from app.schemas.schemas import UserRegister, Token, UserOut
from app.services import auth_service
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ── Shared dependencies ───────────────────────────────────────────────────────

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency used by ALL protected routes.
    User identity is ALWAYS derived from the JWT — never from a client-supplied user_id.
    """
    payload = auth_service.decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("user_id") or payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    if isinstance(user_id, int) or (isinstance(user_id, str) and user_id.isdigit()):
        user = auth_service.get_user_by_id(db, int(user_id))
    else:
        user = auth_service.get_user_by_username(db, str(user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if auth_service.get_user_by_username(db, data.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=auth_service.get_password_hash(data.password),
        role="student",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is disabled")

    token = auth_service.create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
