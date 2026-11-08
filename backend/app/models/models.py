from datetime import datetime, timezone
from sqlalchemy import (
    Boolean, Column, Integer, String, Text, Float,
    DateTime, ForeignKey, JSON, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="student")        # student | admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

    # Relationships (cascade deletes keep student data isolated per user)
    assessment_attempts = relationship("AssessmentAttempt", back_populates="user", cascade="all, delete-orphan")
    learning_path = relationship("LearningPath", back_populates="user", uselist=False, cascade="all, delete-orphan")
    student_knowledge = relationship("StudentKnowledge", back_populates="user", cascade="all, delete-orphan")
    practice_submissions = relationship("PracticeSubmission", back_populates="user", cascade="all, delete-orphan")
    mentor_sessions = relationship("MentorSession", back_populates="user", cascade="all, delete-orphan")
    saved_programs = relationship("SavedProgram", back_populates="user", cascade="all, delete-orphan")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    order = Column(Integer, nullable=False, index=True)
    difficulty = Column(String(20))     # beginner | intermediate | advanced
    icon = Column(String(50), default="📚")
    module_number = Column(Integer, default=1, index=True)
    module_name = Column(String(100), default="Python Fundamentals")
    subtopics = Column(JSON, default=list)
    learning_objectives = Column(JSON, default=list)
    lesson_content = Column(JSON, default=dict)
    prerequisites = Column(JSON, default=list)

    questions = relationship("Question", back_populates="topic")
    practice_problems = relationship("PracticeProblem", back_populates="topic")
    student_knowledge = relationship("StudentKnowledge", back_populates="topic")


class Question(Base):
    """Assessment questions (MCQ only for MVP)."""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    question_type = Column(String(20), default="mcq")   # mcq
    options = Column(JSON)                              # ["opt0", "opt1", ...]
    correct_answer = Column(String(10), nullable=False) # "0" | "1" | "2" | "3" (index)
    difficulty = Column(String(20))
    explanation = Column(Text)

    topic = relationship("Topic", back_populates="questions")


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    skill_level = Column(String(20))                    # beginner | intermediate | advanced
    topic_order = Column(JSON)                          # [topic_id, ...]
    current_topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="learning_path")
    current_topic = relationship("Topic", foreign_keys=[current_topic_id])


class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    started_at = Column(DateTime, default=utc_now)
    completed_at = Column(DateTime, nullable=True)
    score = Column(Float, nullable=True)
    skill_level = Column(String(20), nullable=True)
    answers = Column(JSON)       # {question_id: {answer, correct, correct_answer}}
    topic_scores = Column(JSON)  # {topic_slug: pct}

    user = relationship("User", back_populates="assessment_attempts")


class StudentKnowledge(Base):
    """Per-user, per-topic mastery tracking."""
    __tablename__ = "student_knowledge"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False, index=True)
    mastery_score = Column(Float, default=0.0)
    attempts = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    status = Column(String(20), default="locked")  # locked | available | in_progress | completed
    last_practiced = Column(DateTime, nullable=True)
    completed_lessons = Column(JSON, default=list)
    lesson_completed = Column(Boolean, default=False)
    quiz_completed = Column(Boolean, default=False)
    practice_completed = Column(Boolean, default=False)

    __table_args__ = (UniqueConstraint("user_id", "topic_id"),)

    user = relationship("User", back_populates="student_knowledge")
    topic = relationship("Topic", back_populates="student_knowledge")


class PracticeProblem(Base):
    __tablename__ = "practice_problems"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    difficulty = Column(String(20))         # easy | medium | hard
    starter_code = Column(Text)
    constraints = Column(Text, nullable=True)
    test_cases = Column(JSON)               # [{"call": "fn(args)", "expected_output": "val", "description": "..."}]
    hints = Column(JSON)                    # ["hint1", ...]

    topic = relationship("Topic", back_populates="practice_problems")
    submissions = relationship("PracticeSubmission", back_populates="problem")


class PracticeSubmission(Base):
    __tablename__ = "practice_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    problem_id = Column(Integer, ForeignKey("practice_problems.id"), nullable=False, index=True)
    code = Column(Text)
    passed_cases = Column(Integer, default=0)
    total_cases = Column(Integer, default=0)
    score = Column(Float, default=0.0)
    feedback = Column(Text)
    submitted_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="practice_submissions")
    problem = relationship("PracticeProblem", back_populates="submissions")


class MentorSession(Base):
    __tablename__ = "mentor_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), default="New Session")
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="mentor_sessions")
    messages = relationship("MentorMessage", back_populates="session", cascade="all, delete-orphan")


class MentorMessage(Base):
    __tablename__ = "mentor_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("mentor_sessions.id"), nullable=False, index=True)
    role = Column(String(20))               # user | assistant
    content = Column(Text)
    created_at = Column(DateTime, default=utc_now)

    session = relationship("MentorSession", back_populates="messages")


class SavedProgram(Base):
    __tablename__ = "saved_programs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    language = Column(String(30), default="python")  # python | html | web | javascript
    code = Column(Text, nullable=False)
    extra_data = Column(JSON, nullable=True)         # optional {"css": "...", "js": "..."}
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="saved_programs")
