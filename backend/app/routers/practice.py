from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.models import PracticeProblem, PracticeSubmission, Topic, LearningPath, User
from app.schemas.schemas import SubmissionCreate
from app.routers.auth import get_current_user
from app.services.code_runner import CodeRunner
from app.services import progress_service

router = APIRouter(prefix="/api/practice", tags=["practice"])
_runner = CodeRunner()


def _problem_out(p: PracticeProblem, topic: Optional[Topic]) -> dict:
    cases = p.test_cases or []
    sample_cases = [
        {
            "description": tc.get("description", f"Sample Test {i+1}"),
            "call": tc.get("call", ""),
            "input": tc.get("input", ""),
            "expected_output": tc.get("expected_output", ""),
        }
        for i, tc in enumerate(cases[:2])
    ]
    return {
        "id": p.id,
        "title": p.title,
        "description": p.description,
        "difficulty": p.difficulty,
        "starter_code": p.starter_code,
        "constraints": p.constraints or "Time Limit: 5.0 seconds\nMemory Limit: 128 MB\nStandard Python 3.10+ execution environment",
        "hints": p.hints or [],
        "topic_id": p.topic_id,
        "topic_name": topic.name if topic else "Unknown",
        "test_count": len(cases),
        "sample_cases": sample_cases,
    }


@router.get("/problems")
def get_problems(
    topic_id: Optional[int] = None,
    difficulty: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(PracticeProblem)
    if topic_id:
        query = query.filter(PracticeProblem.topic_id == topic_id)
    if difficulty:
        query = query.filter(PracticeProblem.difficulty == difficulty)

    problems = query.all()
    topics = {t.id: t for t in db.query(Topic).all()}
    return [_problem_out(p, topics.get(p.topic_id)) for p in problems]


@router.get("/problems/recommended")
def get_recommended(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return problems for the user's current topic, falling back to easy problems."""
    lp = db.query(LearningPath).filter(LearningPath.user_id == current_user.id).first()
    topics = {t.id: t for t in db.query(Topic).all()}

    if lp and lp.current_topic_id:
        problems = (
            db.query(PracticeProblem)
            .filter(PracticeProblem.topic_id == lp.current_topic_id)
            .all()
        )
        if problems:
            return [_problem_out(p, topics.get(p.topic_id)) for p in problems]

    # Fallback: all problems
    problems = db.query(PracticeProblem).limit(10).all()
    return [_problem_out(p, topics.get(p.topic_id)) for p in problems]


@router.get("/problems/{problem_id}")
def get_problem(
    problem_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    p = db.query(PracticeProblem).filter(PracticeProblem.id == problem_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Problem not found")
    topic = db.query(Topic).filter(Topic.id == p.topic_id).first()
    return _problem_out(p, topic)


@router.post("/test-run/{problem_id}")
def test_run_code(
    problem_id: int,
    submission: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run code against test cases without saving submission (ByteXL 'Run Code' button)."""
    problem = db.query(PracticeProblem).filter(PracticeProblem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    return _runner.run_with_test_cases(submission.code, problem.test_cases or [])


@router.post("/submissions/{problem_id}")
def submit_code(
    problem_id: int,
    submission: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    problem = db.query(PracticeProblem).filter(PracticeProblem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    result = _runner.run_with_test_cases(submission.code, problem.test_cases or [])

    sub = PracticeSubmission(
        user_id=current_user.id,
        problem_id=problem_id,
        code=submission.code,
        passed_cases=result["passed"],
        total_cases=result["total"],
        score=result["score"],
        feedback=result["feedback"],
    )
    db.add(sub)
    db.commit()

    # Update topic mastery
    progress_service.update_topic_progress(db, current_user.id, problem.topic_id, result["score"])

    return result


@router.get("/submissions")
def my_submissions(
    problem_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(PracticeSubmission).filter(PracticeSubmission.user_id == current_user.id)
    if problem_id:
        query = query.filter(PracticeSubmission.problem_id == problem_id)

    subs = query.order_by(PracticeSubmission.submitted_at.desc()).limit(20).all()
    problems = {p.id: p for p in db.query(PracticeProblem).all()}
    return [
        {
            "id": s.id,
            "problem_id": s.problem_id,
            "problem_title": problems[s.problem_id].title if s.problem_id in problems else "Unknown",
            "score": s.score,
            "passed_cases": s.passed_cases,
            "total_cases": s.total_cases,
            "feedback": s.feedback,
            "code": s.code,
            "submitted_at": s.submitted_at,
        }
        for s in subs
    ]
