from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.models import MentorSession, MentorMessage, LearningPath, Topic, StudentKnowledge, User
from app.schemas.schemas import SessionCreate, MessageCreate, MessageOut
from app.routers.auth import get_current_user
from app.services.ai_service import get_provider

from app.config import settings

router = APIRouter(prefix="/api/mentor", tags=["mentor"])


@router.get("/status")
def get_ai_status(current_user: User = Depends(get_current_user)):
    """Return active AI provider and model for clear student visibility."""
    if settings.AI_PROVIDER == "gemini":
        model_name = settings.GEMINI_MODEL
        desc = f"Connected to Google Gemini ({settings.GEMINI_MODEL})."
    elif settings.AI_PROVIDER == "openai":
        model_name = settings.OPENAI_MODEL
        desc = f"Connected to OpenAI ({settings.OPENAI_MODEL})."
    else:
        model_name = "Offline Pedagogical Mentor"
        desc = "Running in offline demo mode with structured educational responses."

    return {
        "provider": settings.AI_PROVIDER,
        "is_mock": settings.AI_PROVIDER == "mock",
        "model": model_name,
        "description": desc,
    }


@router.get("/sessions")
def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sessions = (
        db.query(MentorSession)
        .filter(MentorSession.user_id == current_user.id)
        .order_by(MentorSession.created_at.desc())
        .all()
    )
    return [{"id": s.id, "title": s.title, "created_at": s.created_at} for s in sessions]


@router.post("/sessions")
def create_session(
    data: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = MentorSession(user_id=current_user.id, title=data.title or "New Session")
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"id": session.id, "title": session.title, "created_at": session.created_at}


@router.get("/sessions/{session_id}/messages", response_model=List[MessageOut])
def get_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = (
        db.query(MentorSession)
        .filter(MentorSession.id == session_id, MentorSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return (
        db.query(MentorMessage)
        .filter(MentorMessage.session_id == session_id)
        .order_by(MentorMessage.created_at)
        .all()
    )


@router.post("/sessions/{session_id}/message")
async def send_message(
    session_id: int,
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = (
        db.query(MentorSession)
        .filter(MentorSession.id == session_id, MentorSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Build personalised context from student's profile
    context = _build_context(db, current_user.id, data.action)
    context["language"] = getattr(data, "language", None) or "en"

    # Persist the user message
    user_msg = MentorMessage(session_id=session_id, role="user", content=data.content)
    db.add(user_msg)
    db.flush()

    # Fetch last 20 messages as conversation history (most recent 20 in chronological order)
    recent_history = (
        db.query(MentorMessage)
        .filter(MentorMessage.session_id == session_id)
        .order_by(MentorMessage.created_at.desc())
        .limit(20)
        .all()
    )
    recent_history.reverse()
    messages = [{"role": m.role, "content": m.content} for m in recent_history]

    # Generate AI response
    provider = get_provider()
    ai_text = await provider.chat(messages, context)

    # Persist AI response
    ai_msg = MentorMessage(session_id=session_id, role="assistant", content=ai_text)
    db.add(ai_msg)

    # Auto-title session from first meaningful user query
    clean_prompt = data.content.strip()
    generic_greetings = {"hello! i'm ready to learn python.", "hello", "hi", "hey", "hey there", "namaste", "vanakkam"}
    if session.title in ("New Session", "New Chat", "Python Inquiry", "Python Learning", "Hello! I'm ready to learn Python.") or session.title.startswith("Hello!"):
        if clean_prompt.lower() not in generic_greetings:
            session.title = clean_prompt[:45] + ("…" if len(clean_prompt) > 45 else "")

    db.commit()
    db.refresh(ai_msg)
    return {
        "id": ai_msg.id,
        "role": "assistant",
        "content": ai_text,
        "language": context.get("language", "en"),
        "created_at": ai_msg.created_at,
        "provider": settings.AI_PROVIDER,
        "is_mock": settings.AI_PROVIDER == "mock",
        "session_title": session.title,
    }


@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = (
        db.query(MentorSession)
        .filter(MentorSession.id == session_id, MentorSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
    return {"success": True}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_context(db: Session, user_id: int, action: str = None) -> dict:
    lp = db.query(LearningPath).filter(LearningPath.user_id == user_id).first()
    context = {"skill_level": "beginner", "current_topic": "Python basics", "weak_topics": [], "action": action}

    if not lp:
        return context

    context["skill_level"] = lp.skill_level or "beginner"

    if lp.current_topic_id:
        ct = db.query(Topic).filter(Topic.id == lp.current_topic_id).first()
        if ct:
            context["current_topic"] = ct.name

    weak = (
        db.query(StudentKnowledge)
        .filter(
            StudentKnowledge.user_id == user_id,
            StudentKnowledge.mastery_score < 50,
            StudentKnowledge.attempts > 0,
        )
        .all()
    )
    if weak:
        topic_ids = [k.topic_id for k in weak]
        weak_topics = db.query(Topic).filter(Topic.id.in_(topic_ids)).all()
        context["weak_topics"] = [t.name for t in weak_topics]

    return context
