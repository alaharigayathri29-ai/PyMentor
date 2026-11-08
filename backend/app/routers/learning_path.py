from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import LearningPath, Topic, StudentKnowledge, User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/learning-path", tags=["learning-path"])


@router.get("/")
def get_learning_path(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lp = db.query(LearningPath).filter(LearningPath.user_id == current_user.id).first()
    if not lp:
        from app.services import progress_service
        lp = progress_service.create_learning_path(db, current_user.id, "beginner", {})

    knowledge_map = {
        k.topic_id: k
        for k in db.query(StudentKnowledge)
        .filter(StudentKnowledge.user_id == current_user.id)
        .all()
    }

    all_topics = db.query(Topic).order_by(Topic.order).all()
    path_ids = set(lp.topic_order or [])

    path_topics = [
        {
            "topic_id": t.id,
            "name": t.name,
            "slug": t.slug,
            "description": t.description,
            "difficulty": t.difficulty,
            "icon": t.icon,
            "order": t.order,
            "status": knowledge_map[t.id].status if t.id in knowledge_map else "locked",
            "mastery_score": round(knowledge_map[t.id].mastery_score, 1) if t.id in knowledge_map else 0.0,
            "attempts": knowledge_map[t.id].attempts if t.id in knowledge_map else 0,
            "is_current": t.id == lp.current_topic_id,
        }
        for t in all_topics
        if t.id in path_ids
    ]

    return {
        "has_path": True,
        "skill_level": lp.skill_level,
        "current_topic_id": lp.current_topic_id,
        "topics": path_topics,
    }


@router.post("/set-topic/{topic_id}")
def set_current_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lp = db.query(LearningPath).filter(LearningPath.user_id == current_user.id).first()
    if not lp:
        raise HTTPException(status_code=404, detail="No learning path found")

    if topic_id not in (lp.topic_order or []):
        raise HTTPException(status_code=400, detail="Topic not in your learning path")

    k = (
        db.query(StudentKnowledge)
        .filter(StudentKnowledge.user_id == current_user.id, StudentKnowledge.topic_id == topic_id)
        .first()
    )
    if k and k.status == "locked":
        raise HTTPException(status_code=400, detail="Topic is still locked. Complete previous topics first.")

    lp.current_topic_id = topic_id
    db.commit()
    return {"success": True, "current_topic_id": topic_id}


@router.get("/curriculum")
def get_curriculum(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all 7 curriculum modules, structured topics, and student mastery."""
    lp = db.query(LearningPath).filter(LearningPath.user_id == current_user.id).first()
    if not lp:
        # Auto-initialize baseline beginner path for new student
        from app.services import progress_service
        lp = progress_service.create_learning_path(db, current_user.id, "beginner", {})

    path_ids = set(lp.topic_order or []) if lp else set()

    knowledge_map = {
        k.topic_id: k
        for k in db.query(StudentKnowledge).filter(StudentKnowledge.user_id == current_user.id).all()
    }

    all_topics = db.query(Topic).order_by(Topic.module_number, Topic.order).all()

    # Group by module number
    modules_dict = {}
    for t in all_topics:
        m_num = t.module_number or 1
        m_name = t.module_name or f"Module {m_num}"
        if m_num not in modules_dict:
            modules_dict[m_num] = {
                "module_number": m_num,
                "module_name": m_name,
                "topics": [],
            }
        
        k = knowledge_map.get(t.id)
        modules_dict[m_num]["topics"].append({
            "id": t.id,
            "name": t.name,
            "slug": t.slug,
            "description": t.description,
            "difficulty": t.difficulty,
            "icon": t.icon,
            "order": t.order,
            "subtopics": t.subtopics or [],
            "learning_objectives": t.learning_objectives or [],
            "status": k.status if k else ("available" if t.order == 1 else "locked"),
            "mastery_score": round(k.mastery_score, 1) if k else 0.0,
            "lesson_completed": k.lesson_completed if k else False,
            "in_path": t.id in path_ids,
            "is_current": lp and t.id == lp.current_topic_id,
        })

    return {
        "skill_level": lp.skill_level if lp else "beginner",
        "current_topic_id": lp.current_topic_id if lp else None,
        "modules": sorted(modules_dict.values(), key=lambda m: m["module_number"]),
    }


@router.get("/topics/{topic_id}")
def get_topic_lesson(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve full structured lesson content for a specific topic."""
    t = db.query(Topic).filter(Topic.id == topic_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Topic not found")

    k = (
        db.query(StudentKnowledge)
        .filter(StudentKnowledge.user_id == current_user.id, StudentKnowledge.topic_id == topic_id)
        .first()
    )

    from app.models.models import PracticeProblem
    problems = (
        db.query(PracticeProblem)
        .filter(PracticeProblem.topic_id == topic_id)
        .all()
    )

    return {
        "id": t.id,
        "name": t.name,
        "slug": t.slug,
        "description": t.description,
        "difficulty": t.difficulty,
        "icon": t.icon,
        "module_number": t.module_number,
        "module_name": t.module_name,
        "subtopics": t.subtopics or [],
        "learning_objectives": t.learning_objectives or [],
        "lesson_content": t.lesson_content or {},
        "status": k.status if k else "available",
        "mastery_score": round(k.mastery_score, 1) if k else 0.0,
        "lesson_completed": k.lesson_completed if k else False,
        "practice_problems": [
            {
                "id": p.id,
                "title": p.title,
                "difficulty": p.difficulty,
                "description": p.description,
            }
            for p in problems
        ],
    }


@router.post("/topics/{topic_id}/complete-lesson")
def complete_topic_lesson(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark lesson study complete and update progression status."""
    k = (
        db.query(StudentKnowledge)
        .filter(StudentKnowledge.user_id == current_user.id, StudentKnowledge.topic_id == topic_id)
        .first()
    )
    if not k:
        k = StudentKnowledge(
            user_id=current_user.id,
            topic_id=topic_id,
            mastery_score=40.0,
            status="in_progress",
            lesson_completed=True,
        )
        db.add(k)
    else:
        k.lesson_completed = True
        k.mastery_score = max(k.mastery_score or 0.0, 40.0)
        if k.status == "locked":
            k.status = "available"
        if k.status == "available":
            k.status = "in_progress"

    db.commit()
    return {
        "success": True,
        "topic_id": topic_id,
        "status": k.status,
        "mastery_score": k.mastery_score,
        "lesson_completed": True,
    }
