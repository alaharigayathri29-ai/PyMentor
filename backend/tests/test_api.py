import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.services.auth_service import get_password_hash
from app.models.models import User, Topic, Question, PracticeProblem

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        t1 = Topic(name="Variables & Data Types", slug="variables", description="Test variables", order=1, difficulty="beginner", icon="📦")
        t2 = Topic(name="Operators & Expressions", slug="operators", description="Test operators", order=2, difficulty="beginner", icon="🧮")
        db.add_all([t1, t2])
        db.flush()

        q1 = Question(topic_id=t1.id, text="What is type(1)?", options=["int", "str", "float", "bool"], correct_answer="0", difficulty="easy", explanation="1 is int")
        q2 = Question(topic_id=t1.id, text="What is type('a')?", options=["int", "str", "float", "bool"], correct_answer="1", difficulty="easy", explanation="'a' is str")
        db.add_all([q1, q2])

        p1 = PracticeProblem(
            topic_id=t1.id,
            title="Add Two Numbers",
            description="Write a function add(a, b) that returns a + b",
            difficulty="easy",
            starter_code="def add(a, b):\n    pass",
            test_cases=[
                {"call": "add(2, 3)", "expected_output": "5", "description": "Positive numbers"},
                {"call": "add(-1, 1)", "expected_output": "0", "description": "Negative and positive"},
            ],
            hints=["Use the + operator"],
        )
        db.add(p1)

        admin = User(
            username="admin",
            email="admin@test.com",
            hashed_password=get_password_hash("admin123"),
            role="admin",
        )
        db.add(admin)
        db.commit()
    finally:
        db.close()


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "healthy"}


def test_auth_flow():
    res = client.post("/api/auth/register", json={
        "username": "student1",
        "email": "student1@test.com",
        "password": "password123",
    })
    assert res.status_code == 201
    me = res.json()
    assert me["username"] == "student1"
    assert me["role"] == "student"

    # Login
    res = client.post("/api/auth/login", data={
        "username": "student1",
        "password": "password123",
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    token = data["access_token"]

    # Get /me
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    me = res.json()
    assert me["username"] == "student1"


def test_assessment_flow():
    res = client.post("/api/auth/login", data={"username": "student1", "password": "password123"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/assessment/questions", headers=headers)
    assert res.status_code == 200
    qs = res.json()
    assert len(qs) >= 2

    # Send list of answers
    payload = {"answers": [{"question_id": q["id"], "answer": "0"} for q in qs]}
    res = client.post("/api/assessment/submit", json=payload, headers=headers)
    assert res.status_code == 200
    result = res.json()
    assert "skill_level" in result
    assert "score" in result
    assert result["total_questions"] == len(qs)

    res = client.get("/api/assessment/result", headers=headers)
    assert res.status_code == 200
    assert res.json()["skill_level"] is not None


def test_learning_path_flow():
    res = client.post("/api/auth/login", data={"username": "student1", "password": "password123"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/learning-path/", headers=headers)
    assert res.status_code == 200
    lp = res.json()
    assert lp["has_path"] is True
    assert "topics" in lp
    assert len(lp["topics"]) > 0


def test_mentor_chat():
    res = client.post("/api/auth/login", data={"username": "student1", "password": "password123"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/mentor/sessions", json={"title": "Python Help"}, headers=headers)
    assert res.status_code == 200
    sess = res.json()
    session_id = sess["id"]

    res = client.post(f"/api/mentor/sessions/{session_id}/message", json={"content": "How do variables work in Python?"}, headers=headers)
    assert res.status_code == 200
    chat_resp = res.json()
    assert chat_resp["role"] == "assistant"
    assert "content" in chat_resp
    assert len(chat_resp["content"]) > 0


def test_code_execution():
    res = client.post("/api/auth/login", data={"username": "student1", "password": "password123"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/practice/problems", headers=headers)
    assert res.status_code == 200
    probs = res.json()
    assert len(probs) > 0
    prob_id = probs[0]["id"]

    valid_code = "def add(a, b):\n    return a + b\n"
    res = client.post(f"/api/practice/submissions/{prob_id}", json={"code": valid_code}, headers=headers)
    assert res.status_code == 200
    sub_res = res.json()
    assert sub_res["passed"] == sub_res["total"]
    assert sub_res["score"] == 100.0


def test_progress_dashboard():
    res = client.post("/api/auth/login", data={"username": "student1", "password": "password123"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/progress/", headers=headers)
    assert res.status_code == 200
    prog = res.json()
    assert "skill_level" in prog
    assert "overall_progress" in prog
    assert "topics" in prog
    assert len(prog["topics"]) > 0


def test_admin_access():
    res = client.post("/api/auth/login", data={"username": "student1", "password": "password123"})
    s_token = res.json()["access_token"]
    res = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {s_token}"})
    assert res.status_code == 403

    res = client.post("/api/auth/login", data={"username": "admin", "password": "admin123"})
    a_token = res.json()["access_token"]
    res = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {a_token}"})
    assert res.status_code == 200
    stats = res.json()
    assert "total_students" in stats
    assert "total_submissions" in stats


def test_workspace_flow():
    res = client.post("/api/auth/login", data={"username": "student1", "password": "password123"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Run custom code
    run_res = client.post("/api/workspace/run", json={"code": "print('Hello from workspace')\nx = 2 + 3\nprint(f'Sum: {x}')"}, headers=headers)
    assert run_res.status_code == 200
    run_data = run_res.json()
    assert run_data["success"] is True
    assert "Hello from workspace" in run_data["stdout"]
    assert "Sum: 5" in run_data["stdout"]

    # 2. Save program
    save_res = client.post("/api/workspace/programs", json={
        "title": "My Calculator Script",
        "description": "Simple calculator practice",
        "code": "def calc(a, b):\n    return a * b\nprint(calc(6, 7))",
    }, headers=headers)
    assert save_res.status_code == 201
    prog = save_res.json()
    prog_id = prog["id"]
    assert prog["title"] == "My Calculator Script"

    # 3. List saved programs
    list_res = client.get("/api/workspace/programs", headers=headers)
    assert list_res.status_code == 200
    progs = list_res.json()
    assert any(p["id"] == prog_id for p in progs)

    # 4. Update saved program
    update_res = client.put(f"/api/workspace/programs/{prog_id}", json={
        "title": "Updated Calculator Script",
        "code": "def calc(a, b):\n    return a + b\nprint(calc(6, 7))",
    }, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Updated Calculator Script"

    # 5. Delete saved program
    del_res = client.delete(f"/api/workspace/programs/{prog_id}", headers=headers)
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

