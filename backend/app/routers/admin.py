from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.models import (
    User, LearningPath, AssessmentAttempt, PracticeSubmission,
    MentorSession, MentorMessage, StudentKnowledge, Topic, PracticeProblem, Question
)
from app.routers.auth import require_admin
from app.services import auth_service, progress_service
from app.seed_data import seed_demo_students

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users")
def list_users(
    q: Optional[str] = Query(None, description="Search by username or email"),
    skill_level: Optional[str] = Query(None, description="Filter by skill level"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """List students with search, filters, and activity metrics."""
    query = db.query(User).filter(User.role == "student")

    if q:
        query = query.filter(or_(User.username.ilike(f"%{q}%"), User.email.ilike(f"%{q}%")))

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    students = query.order_by(User.created_at.desc()).all()

    result = []
    for u in students:
        lp = db.query(LearningPath).filter(LearningPath.user_id == u.id).first()
        if skill_level and (not lp or lp.skill_level != skill_level):
            continue

        latest_attempt = (
            db.query(AssessmentAttempt)
            .filter(AssessmentAttempt.user_id == u.id)
            .order_by(AssessmentAttempt.completed_at.desc())
            .first()
        )
        attempt_count = db.query(AssessmentAttempt).filter(AssessmentAttempt.user_id == u.id).count()

        sub_stats = (
            db.query(
                func.count(PracticeSubmission.id).label("count"),
                func.avg(PracticeSubmission.score).label("avg_score")
            )
            .filter(PracticeSubmission.user_id == u.id)
            .first()
        )

        session_count = db.query(MentorSession).filter(MentorSession.user_id == u.id).count()

        latest_sub = (
            db.query(PracticeSubmission)
            .filter(PracticeSubmission.user_id == u.id)
            .order_by(PracticeSubmission.submitted_at.desc())
            .first()
        )
        last_active = latest_sub.submitted_at if latest_sub else u.created_at

        result.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "created_at": u.created_at,
            "is_active": u.is_active,
            "skill_level": lp.skill_level if lp else None,
            "has_assessment": attempt_count > 0,
            "assessment_score": latest_attempt.score if latest_attempt else None,
            "submission_count": sub_stats.count or 0,
            "avg_submission_score": round(sub_stats.avg_score or 0, 1),
            "session_count": session_count,
            "last_active": last_active,
        })
    return result


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Aggregate statistics for admin dashboard."""
    total_students = db.query(User).filter(User.role == "student").count()
    active_students = db.query(User).filter(User.role == "student", User.is_active == True).count()
    total_assessments = db.query(AssessmentAttempt).count()
    total_submissions = db.query(PracticeSubmission).count()
    total_sessions = db.query(MentorSession).count()

    level_rows = (
        db.query(LearningPath.skill_level, func.count(LearningPath.id))
        .group_by(LearningPath.skill_level)
        .all()
    )
    level_dist = {row[0]: row[1] for row in level_rows if row[0]}

    avg_score = db.query(func.avg(AssessmentAttempt.score)).scalar()
    avg_submission_score = db.query(func.avg(PracticeSubmission.score)).scalar()

    # Pass rate: submissions with score >= 70
    passing_subs = db.query(PracticeSubmission).filter(PracticeSubmission.score >= 70).count()
    pass_rate = round((passing_subs / total_submissions * 100) if total_submissions > 0 else 0, 1)

    return {
        "total_students": total_students,
        "active_students": active_students,
        "total_assessments": total_assessments,
        "total_submissions": total_submissions,
        "total_mentor_sessions": total_sessions,
        "skill_level_distribution": level_dist,
        "average_assessment_score": round(avg_score or 0, 1),
        "average_submission_score": round(avg_submission_score or 0, 1),
        "submission_pass_rate": pass_rate,
    }


@router.get("/users/{user_id}/detail")
def get_student_detail(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Detailed student dossier including assessment history and topic mastery."""
    user = db.query(User).filter(User.id == user_id, User.role == "student").first()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")

    lp = db.query(LearningPath).filter(LearningPath.user_id == user_id).first()
    topics = {t.id: t for t in db.query(Topic).all()}

    # Assessment history
    attempts = (
        db.query(AssessmentAttempt)
        .filter(AssessmentAttempt.user_id == user_id)
        .order_by(AssessmentAttempt.completed_at.desc())
        .all()
    )

    # Topic Knowledge
    knowledge = (
        db.query(StudentKnowledge)
        .filter(StudentKnowledge.user_id == user_id)
        .all()
    )

    knowledge_list = []
    for k in knowledge:
        top = topics.get(k.topic_id)
        knowledge_list.append({
            "topic_id": k.topic_id,
            "topic_name": top.name if top else "Unknown",
            "topic_slug": top.slug if top else "",
            "icon": top.icon if top else "📚",
            "mastery_score": k.mastery_score,
            "status": k.status,
            "attempts": k.attempts,
            "correct_count": k.correct_count,
            "last_practiced": k.last_practiced,
        })

    # Summary
    sub_count = db.query(PracticeSubmission).filter(PracticeSubmission.user_id == user_id).count()
    pass_count = db.query(PracticeSubmission).filter(PracticeSubmission.user_id == user_id, PracticeSubmission.score >= 70).count()
    session_count = db.query(MentorSession).filter(MentorSession.user_id == user_id).count()

    current_topic_name = "None"
    if lp and lp.current_topic_id in topics:
        current_topic_name = topics[lp.current_topic_id].name

    return {
        "profile": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at,
        },
        "learning_path": {
            "skill_level": lp.skill_level if lp else "unassessed",
            "current_topic": current_topic_name,
            "topic_order": lp.topic_order if lp else [],
        },
        "metrics": {
            "submissions_count": sub_count,
            "passed_submissions": pass_count,
            "sessions_count": session_count,
        },
        "assessment_attempts": [
            {
                "id": a.id,
                "score": a.score,
                "skill_level": a.skill_level,
                "completed_at": a.completed_at,
                "topic_scores": a.topic_scores or {},
            }
            for a in attempts
        ],
        "mastery_breakdown": knowledge_list,
        "summary": progress_service.get_progress_summary(db, user_id),
    }


@router.get("/users/{user_id}/submissions")
def get_student_submissions(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """View all code submissions for a specific student."""
    user = db.query(User).filter(User.id == user_id, User.role == "student").first()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")

    subs = (
        db.query(PracticeSubmission)
        .filter(PracticeSubmission.user_id == user_id)
        .order_by(PracticeSubmission.submitted_at.desc())
        .all()
    )
    problems = {p.id: p for p in db.query(PracticeProblem).all()}

    return [
        {
            "id": s.id,
            "problem_id": s.problem_id,
            "problem_title": problems[s.problem_id].title if s.problem_id in problems else "Unknown Problem",
            "difficulty": problems[s.problem_id].difficulty if s.problem_id in problems else "medium",
            "code": s.code,
            "passed_cases": s.passed_cases,
            "total_cases": s.total_cases,
            "score": s.score,
            "feedback": s.feedback,
            "submitted_at": s.submitted_at,
        }
        for s in subs
    ]


@router.get("/users/{user_id}/sessions")
def get_student_sessions(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """View AI mentor conversations for a specific student."""
    user = db.query(User).filter(User.id == user_id, User.role == "student").first()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")

    sessions = (
        db.query(MentorSession)
        .filter(MentorSession.user_id == user_id)
        .order_by(MentorSession.created_at.desc())
        .all()
    )

    results = []
    for s in sessions:
        msgs = (
            db.query(MentorMessage)
            .filter(MentorMessage.session_id == s.id)
            .order_by(MentorMessage.created_at.asc())
            .all()
        )
        results.append({
            "id": s.id,
            "title": s.title,
            "topic": s.title,
            "created_at": s.created_at,
            "message_count": len(msgs),
            "messages": [
                {"id": m.id, "role": m.role, "content": m.content, "created_at": m.created_at}
                for m in msgs
            ]
        })
    return results


@router.post("/seed-demo-students")
def trigger_seed_demo_students(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Admin trigger to populate 4 realistic demo student accounts."""
    count = seed_demo_students(db)
    return {
        "message": f"Successfully created/verified {count} demo student accounts.",
        "students": [
            {"username": "priya_beginner", "email": "priya@example.com", "level": "beginner", "password": "student123"},
            {"username": "rahul_intermediate", "email": "rahul@example.com", "level": "intermediate", "password": "student123"},
            {"username": "ananya_advanced", "email": "ananya@example.com", "level": "advanced", "password": "student123"},
            {"username": "vikram_code", "email": "vikram@example.com", "level": "beginner", "password": "student123"},
        ]
    }


@router.post("/impersonate/{user_id}")
def impersonate_student(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Generate a valid JWT token to impersonate a student in the UI."""
    target_user = db.query(User).filter(User.id == user_id, User.role == "student").first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Student not found")

    token = auth_service.create_access_token(
        data={"sub": str(target_user.id), "role": target_user.role, "impersonated_by": admin.id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": target_user.id,
            "username": target_user.username,
            "email": target_user.email,
            "role": target_user.role,
        }
    }


@router.patch("/users/{user_id}/toggle-active")
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id, User.role == "student").first()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")
    user.is_active = not user.is_active
    db.commit()
    return {"id": user.id, "is_active": user.is_active}


# ── Curriculum Creator Endpoints (Create Problems & Assessment Questions) ──────

@router.get("/content-items")
def list_curriculum_content(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Retrieve all topics, practice problems, and assessment questions for admin editing."""
    topics = db.query(Topic).order_by(Topic.order).all()
    problems = db.query(PracticeProblem).order_by(PracticeProblem.id.desc()).all()
    questions = db.query(Question).order_by(Question.id.desc()).all()
    topic_map = {t.id: t.name for t in topics}

    return {
        "topics": [{"id": t.id, "name": t.name, "slug": t.slug, "icon": t.icon} for t in topics],
        "problems": [
            {
                "id": p.id,
                "title": p.title,
                "topic_id": p.topic_id,
                "topic_name": topic_map.get(p.topic_id, "Unknown"),
                "difficulty": p.difficulty,
                "test_count": len(p.test_cases or []),
            }
            for p in problems
        ],
        "questions": [
            {
                "id": q.id,
                "text": q.text,
                "topic_id": q.topic_id,
                "topic_name": topic_map.get(q.topic_id, "Unknown"),
                "difficulty": q.difficulty,
            }
            for q in questions
        ],
    }


@router.post("/problems")
def create_problem(
    data: dict,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Create a new coding challenge practice problem."""
    title = data.get("title", "").strip()
    if not title:
        raise HTTPException(status_code=400, detail="Title is required")

    topic_id = data.get("topic_id")
    if not topic_id:
        topic = db.query(Topic).first()
        topic_id = topic.id if topic else 1

    problem = PracticeProblem(
        topic_id=int(topic_id),
        title=title,
        description=data.get("description", "Write a Python function to solve this problem."),
        difficulty=data.get("difficulty", "easy"),
        starter_code=data.get("starter_code", "# Write your code here\n"),
        test_cases=data.get("test_cases", [{"call": "solution()", "expected_output": "True", "description": "Sample test"}]),
        hints=data.get("hints", ["Think about edge cases"]),
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return {"id": problem.id, "title": problem.title, "message": "Practice problem created successfully!"}


@router.delete("/problems/{problem_id}")
def delete_problem(
    problem_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    problem = db.query(PracticeProblem).filter(PracticeProblem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    db.delete(problem)
    db.commit()
    return {"message": "Problem deleted"}


@router.post("/questions")
def create_question(
    data: dict,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Create a new MCQ assessment question."""
    text = data.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Question text is required")

    options = data.get("options", ["Option A", "Option B", "Option C", "Option D"])
    correct = str(data.get("correct_answer", "0"))

    topic_id = data.get("topic_id")
    if not topic_id:
        topic = db.query(Topic).first()
        topic_id = topic.id if topic else 1

    q = Question(
        topic_id=int(topic_id),
        text=text,
        question_type="mcq",
        options=options,
        correct_answer=correct,
        difficulty=data.get("difficulty", "easy"),
        explanation=data.get("explanation", "Review core fundamentals."),
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return {"id": q.id, "text": q.text, "message": "Assessment question created successfully!"}


@router.delete("/questions/{question_id}")
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(q)
    db.commit()
    return {"message": "Question deleted"}


