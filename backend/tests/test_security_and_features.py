import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.code_runner import CodeRunner

client = TestClient(app)
runner = CodeRunner()


def test_code_runner_security_blocking():
    # 1. Block os import
    res = runner.run_custom_script("import os\nprint(os.getcwd())")
    assert res["success"] is False
    assert "Safety Error" in res["stderr"]

    # 2. Block subprocess import
    res = runner.run_custom_script("import subprocess\nsubprocess.run('ls')")
    assert res["success"] is False
    assert "Safety Error" in res["stderr"]

    # 3. Block socket and urllib network calls
    res = runner.run_custom_script("import socket\ns = socket.socket()")
    assert res["success"] is False
    assert "Safety Error" in res["stderr"]

    res = runner.run_custom_script("import urllib.request\nurllib.request.urlopen('http://google.com')")
    assert res["success"] is False
    assert "Safety Error" in res["stderr"]

    # 4. Block eval/exec
    res = runner.run_custom_script("eval('1 + 1')")
    assert res["success"] is False
    assert "restricted" in res["stderr"]

    # 5. Block dunder reflection
    res = runner.run_custom_script("x = ().__class__.__bases__[0].__subclasses__()")
    assert res["success"] is False
    assert "restricted" in res["stderr"]

    # 6. Allow safe python computation
    res = runner.run_custom_script("numbers = [1, 2, 3, 4, 5]\nprint('Sum:', sum(numbers))")
    assert res["success"] is True
    assert "Sum: 15" in res["stdout"]


def test_curriculum_endpoint():
    # Sync full curriculum into test DB
    from app.database import get_db
    from app.seed_data import sync_curriculum_data
    # Get test session from override
    db_gen = app.dependency_overrides[get_db]()
    test_db = next(db_gen)
    sync_curriculum_data(test_db)

    # Login as student
    client.post("/api/auth/register", json={"username": "curric_tester", "email": "curric@test.com", "password": "student123"})
    login_res = client.post("/api/auth/login", data={"username": "curric_tester", "password": "student123"})

    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/learning-path/curriculum", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "modules" in data
    assert len(data["modules"]) >= 7
    # Verify module names
    mod_names = [m["module_name"] for m in data["modules"]]
    assert "Python Fundamentals" in mod_names
    assert "Control Flow" in mod_names
    assert "Data Structures" in mod_names


def test_student_isolation():
    # Register Student A
    client.post("/api/auth/register", json={"username": "student_alpha", "email": "alpha@test.com", "password": "password123"})
    tok_a = client.post("/api/auth/login", data={"username": "student_alpha", "password": "password123"}).json()["access_token"]
    head_a = {"Authorization": f"Bearer {tok_a}"}

    # Register Student B
    client.post("/api/auth/register", json={"username": "student_beta", "email": "beta@test.com", "password": "password123"})
    tok_b = client.post("/api/auth/login", data={"username": "student_beta", "password": "password123"}).json()["access_token"]
    head_b = {"Authorization": f"Bearer {tok_b}"}

    # Student A creates a mentor session
    sess_res = client.post("/api/mentor/sessions", json={"title": "Alpha Private Chat"}, headers=head_a)
    assert sess_res.status_code == 200
    sess_id = sess_res.json()["id"]

    # Student B attempts to read Student A's session messages -> Must be 404
    bad_res = client.get(f"/api/mentor/sessions/{sess_id}/messages", headers=head_b)
    assert bad_res.status_code == 404

    # Student B attempts to post message to Student A's session -> Must be 404
    bad_post = client.post(f"/api/mentor/sessions/{sess_id}/message", json={"content": "Sneak"}, headers=head_b)
    assert bad_post.status_code == 404

    # Student A saves a program in playground
    prog_res = client.post("/api/workspace/programs", json={"title": "Alpha Secrets", "code": "x = 42"}, headers=head_a)
    assert prog_res.status_code == 201
    prog_id = prog_res.json()["id"]

    # Student B attempts to read Student A's program -> Must be 404
    bad_prog = client.get(f"/api/workspace/programs/{prog_id}", headers=head_b)
    assert bad_prog.status_code == 404

    # Student B cannot access Admin APIs -> Must be 403 Forbidden
    adm_res = client.get("/api/admin/users", headers=head_b)
    assert adm_res.status_code == 403
