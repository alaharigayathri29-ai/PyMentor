from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.database import get_db
from app.models.models import Question, Topic, AssessmentAttempt, User
from app.schemas.schemas import AssessmentSubmit, AssessmentResult
from app.routers.auth import get_current_user
from app.services import progress_service
from app.curriculum.polyglot_assessment import POLYGLOT_QUESTIONS

router = APIRouter(prefix="/api/assessment", tags=["assessment"])


@router.get("/questions")
def get_questions(
    course: Optional[str] = Query("python", description="Language course: python, c, cpp, java"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return assessment questions for specified course (Python, C, Modern C++, Enterprise Java)."""
    course_clean = (course or "python").lower().strip()

    if course_clean in POLYGLOT_QUESTIONS:
        return [
            {
                "id": q["id"],
                "text": q["text"],
                "type": q["type"],
                "options": q["options"],
                "difficulty": q["difficulty"],
                "topic": q["topic"],
                "topic_slug": q["topic_slug"],
                "module_number": 1,
                "course": course_clean,
            }
            for q in POLYGLOT_QUESTIONS[course_clean]
        ]

    # Default Python Diagnostic Questions from DB
    core_slugs = ["variables", "operators"]
    topics = {t.id: t for t in db.query(Topic).filter(Topic.slug.in_(core_slugs)).all()}
    if not topics:
        topics = {t.id: t for t in db.query(Topic).limit(2).all()}

    questions = (
        db.query(Question)
        .filter(Question.topic_id.in_(topics.keys()))
        .order_by(Question.topic_id, Question.id)
        .all()
    )

    return [
        {
            "id": q.id,
            "text": q.text,
            "type": q.question_type,
            "options": q.options,
            "difficulty": q.difficulty,
            "topic": topics[q.topic_id].name if q.topic_id in topics else "General",
            "topic_slug": topics[q.topic_id].slug if q.topic_id in topics else "general",
            "module_number": 1 if (topics.get(q.topic_id) and topics[q.topic_id].slug == "variables") else 2,
            "course": "python",
        }
        for q in questions
    ]



@router.post("/submit", response_model=AssessmentResult)
def submit_assessment(
    submission: AssessmentSubmit,
    course: Optional[str] = Query("python"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Grade submitted answers, determine skill level, create learning path."""
    db_questions: Dict[int, Question] = {q.id: q for q in db.query(Question).all()}
    topics: Dict[int, Topic] = {t.id: t for t in db.query(Topic).all()}

    # Merge polyglot assessment questions into lookup dictionary
    poly_lookup = {}
    for c_key, q_list in POLYGLOT_QUESTIONS.items():
        for q in q_list:
            poly_lookup[q["id"]] = q

    topic_correct: Dict[str, List[bool]] = {}
    answers_map: Dict[str, dict] = {}
    total_correct = 0

    for ans in submission.answers:
        q_id = ans.question_id
        is_correct = False
        correct_answer = ""
        explanation = ""
        topic_slug = "general"

        if q_id in poly_lookup:
            q = poly_lookup[q_id]
            correct_answer = str(q.get("correct_answer", "")).strip()
            explanation = q.get("explanation", "")
            topic_slug = q.get("topic_slug", "polyglot")
            is_correct = ans.answer.strip() == correct_answer
        elif q_id in db_questions:
            q = db_questions[q_id]
            correct_answer = str(q.correct_answer).strip()
            explanation = q.explanation or ""
            topic = topics.get(q.topic_id)
            topic_slug = topic.slug if topic else "general"
            is_correct = ans.answer.strip() == correct_answer
        else:
            continue

        if is_correct:
            total_correct += 1

        topic_correct.setdefault(topic_slug, []).append(is_correct)

        answers_map[str(q_id)] = {
            "answer": ans.answer,
            "correct": is_correct,
            "correct_answer": correct_answer,
            "explanation": explanation,
        }

    total_q = len(submission.answers)
    score_pct = (total_correct / total_q * 100) if total_q else 0.0

    # Skill level thresholds
    if score_pct >= 71:
        skill_level = "advanced"
    elif score_pct >= 41:
        skill_level = "intermediate"
    else:
        skill_level = "beginner"

    # Per-topic scores
    topic_scores = {
        slug: round(sum(1 for r in results if r) / len(results) * 100, 1)
        for slug, results in topic_correct.items()
    }

    # Persist attempt
    attempt = AssessmentAttempt(
        user_id=current_user.id,
        completed_at=datetime.now(timezone.utc),
        score=round(score_pct, 1),
        skill_level=skill_level,
        answers=answers_map,
        topic_scores=topic_scores,
    )
    db.add(attempt)
    db.commit()

    # Build personalised learning path
    progress_service.create_learning_path(db, current_user.id, skill_level, topic_scores)

    return AssessmentResult(
        score=round(score_pct, 1),
        skill_level=skill_level,
        topic_scores=topic_scores,
        total_questions=total_q,
        correct_answers=total_correct,
    )


@router.get("/result")
def get_latest_result(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Latest completed assessment result for the logged-in user."""
    attempt = (
        db.query(AssessmentAttempt)
        .filter(
            AssessmentAttempt.user_id == current_user.id,
            AssessmentAttempt.completed_at.isnot(None),
        )
        .order_by(AssessmentAttempt.completed_at.desc())
        .first()
    )
    if not attempt:
        return None

    answers_dict = attempt.answers or {}
    total_q = len(answers_dict)
    correct_count = sum(1 for a in answers_dict.values() if isinstance(a, dict) and a.get("correct"))

    return {
        "id": attempt.id,
        "score": attempt.score,
        "skill_level": attempt.skill_level,
        "topic_scores": attempt.topic_scores or {},
        "answers": answers_dict,
        "completed_at": attempt.completed_at,
        "total_questions": total_q,
        "correct_answers": correct_count,
    }
