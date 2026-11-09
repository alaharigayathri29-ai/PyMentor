from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# ── Auth ────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Assessment ───────────────────────────────────────────────────────────────

class AnswerSubmission(BaseModel):
    question_id: int
    answer: str      # index string: "0" | "1" | "2" | "3"


class AssessmentSubmit(BaseModel):
    answers: List[AnswerSubmission]


class AssessmentResult(BaseModel):
    score: float
    skill_level: str
    topic_scores: Dict[str, float]
    total_questions: int
    correct_answers: int


# ── Learning Path ────────────────────────────────────────────────────────────

class TopicInPath(BaseModel):
    topic_id: int
    name: str
    slug: str
    description: Optional[str]
    difficulty: str
    icon: str
    order: int
    status: str
    mastery_score: float
    attempts: int
    is_current: bool


class LearningPathOut(BaseModel):
    has_path: bool
    skill_level: Optional[str] = None
    current_topic_id: Optional[int] = None
    topics: List[TopicInPath] = []


# ── Mentor ───────────────────────────────────────────────────────────────────

class SessionCreate(BaseModel):
    title: Optional[str] = "New Session"


class MessageCreate(BaseModel):
    content: str
    action: Optional[str] = None  # explain_differently | hint | practice_problem
    language: Optional[str] = "en"


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Practice ─────────────────────────────────────────────────────────────────

class SubmissionCreate(BaseModel):
    code: str


class TestCaseResult(BaseModel):
    passed: bool
    description: Optional[str] = ""
    input: Optional[str] = ""
    expected: Optional[str] = ""
    actual: Optional[str] = ""
    error: Optional[str] = None


class SubmissionResult(BaseModel):
    passed: int
    total: int
    score: float
    feedback: str
    results: List[Dict[str, Any]]


# ── Progress ─────────────────────────────────────────────────────────────────

class TopicProgress(BaseModel):
    topic_id: int
    topic_name: str
    slug: str
    difficulty: str
    icon: str
    status: str
    mastery_score: float
    attempts: int
    in_path: bool


class ProgressSummary(BaseModel):
    skill_level: Optional[str]
    overall_progress: float
    current_topic: Optional[str]
    completed_count: int
    total_topics: int
    weak_topics: List[str]
    recommended_next: Optional[str]
    topics: List[TopicProgress]


# ── Workspace / Saved Programs ───────────────────────────────────────────────

class SavedProgramCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    language: Optional[str] = "python"
    code: str
    extra_data: Optional[Dict[str, Any]] = None


class SavedProgramUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    language: Optional[str] = None
    code: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class SavedProgramOut(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str] = ""
    language: str
    code: str
    extra_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkspaceRunRequest(BaseModel):
    code: str
    language: Optional[str] = "python"
    stdin_input: Optional[str] = ""


class WorkspaceRunResult(BaseModel):
    success: bool
    stdout: str
    output: Optional[str] = ""
    stderr: Optional[str] = ""
    error: Optional[str] = None
    execution_time_ms: float
