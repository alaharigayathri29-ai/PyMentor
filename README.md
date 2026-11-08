# AI Programming Mentor

A full-stack, multi-user AI programming mentor that teaches Python interactively. Students get personalised assessments, AI mentor chat, coding practice with real test-case evaluation, and full progress tracking.

---

## Project Structure

```
ai-mentor/
├── backend/               # FastAPI REST API
│   ├── app/
│   │   ├── main.py        # App entry point, CORS, router mounting
│   │   ├── config.py      # Pydantic settings (reads .env)
│   │   ├── database.py    # SQLAlchemy engine + session factory
│   │   ├── models/        # ORM models (User, Topic, Question, …)
│   │   ├── schemas/       # Pydantic request/response schemas
│   │   ├── routers/       # Route handlers
│   │   │   ├── auth.py
│   │   │   ├── assessment.py
│   │   │   ├── learning_path.py
│   │   │   ├── mentor.py
│   │   │   ├── practice.py
│   │   │   ├── progress.py
│   │   │   └── admin.py
│   │   ├── services/
│   │   │   ├── auth_service.py    # JWT + bcrypt
│   │   │   ├── ai_service.py      # AIProvider abstraction + Mock + OpenAI
│   │   │   ├── code_runner.py     # AST-safe subprocess execution
│   │   │   └── progress_service.py
│   │   └── seed_data.py   # Topics, questions, problems, admin user
│   ├── requirements.txt
│   └── .env.example
└── frontend/              # Vanilla HTML/CSS/JS SPA
    ├── index.html
    ├── css/style.css
    └── js/
        ├── api.js          # API client with JWT
        ├── app.js          # SPA router + global state
        ├── auth.js
        ├── dashboard.js
        ├── assessment.js
        ├── learning-path.js
        ├── mentor.js
        ├── practice.js
        ├── progress.js
        └── admin.js
```

---

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env — at minimum set a strong SECRET_KEY

# Start the server (auto-seeds DB on first run)
uvicorn app.main:app --reload
```

API will be available at `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
cd frontend

# Serve with Python's built-in server
python -m http.server 8080


# Or use any static server:
# npx serve .
```

Open `http://localhost:8080` in your browser.

---

## Configuration (`.env`)

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./ai_mentor.db` | Database connection string |
| `SECRET_KEY` | *(dev key)* | **Change in production!** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | JWT expiry (24 hours) |
| `AI_PROVIDER` | `gemini` | `mock`, `gemini`, or `openai` |
| `GEMINI_API_KEY` | *(empty)* | Required if `AI_PROVIDER=gemini` |
| `GEMINI_MODEL` | `gemini-3.5-flash` | Gemini model name |
| `OPENAI_API_KEY` | *(empty)* | Required if `AI_PROVIDER=openai` |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model name |
| `ADMIN_EMAIL` | `admin@example.com` | Auto-created admin email |
| `ADMIN_PASSWORD` | `admin123` | Auto-created admin password |

### Using Google Gemini

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-key
GEMINI_MODEL=gemini-3.5-flash
```

### Using OpenAI

```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

### Using PostgreSQL

```env
DATABASE_URL=postgresql://user:password@localhost:5432/ai_mentor_db
```

---

## Default Credentials

| Role | Username | Password | Notes |
|---|---|---|---|
| Admin | `admin` | `admin123` | Full monitoring & inspection |
| Student (Beginner) | `priya_beginner` | `student123` | 42% quiz score, 2 submissions |
| Student (Intermediate) | `rahul_intermediate` | `student123` | 68% quiz score, 4 submissions |
| Student (Advanced) | `ananya_advanced` | `student123` | 92% quiz score, 5 submissions |
| Student (Beginner/Errors) | `vikram_code` | `student123` | 46% quiz score, logic error cases |

> **Pro-Tip**: Use the **Switch Profile** dropdown located at the top-right bar of the UI to seamlessly toggle between Admin and students without re-entering credentials!


---

## Features

### Student Flow
1. **Register / Login** — secure JWT authentication
2. **Assessment** — 25-question MCQ quiz covering 7 Python topics
3. **Skill Level** — Beginner / Intermediate / Advanced (based on score)
4. **Learning Path** — personalised topic sequence with lock/unlock progression
5. **AI Mentor** — chat interface with Explain Differently / Hint / Practice Problem actions
6. **Code Practice** — write Python, test against real test cases, get feedback
7. **Progress Dashboard** — mastery per topic, weak areas, recommendations

### Security
- All API routes validate identity from the JWT token, never from client-supplied IDs
- Passwords hashed with bcrypt (passlib)
- Multi-user data isolation enforced at the database level with `user_id` FKs

### AI Architecture
```
AI_PROVIDER env var
    ├── "openai" + OPENAI_API_KEY  →  OpenAIProvider (real LLM)
    └── "mock" (default)           →  MockMentorProvider
                                       (keyword-aware, level-adaptive,
                                        works with NO API key)
```

### Code Execution
- Syntax validated with `ast.parse` before execution
- Dangerous imports blocked via AST walk
- Runs in an isolated subprocess with a 5-second timeout
- Clearly separated in `services/code_runner.py` — swap for Judge0/Piston in production

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Get JWT token |
| GET | `/api/auth/me` | Current user |
| GET | `/api/assessment/questions` | All assessment questions |
| POST | `/api/assessment/submit` | Submit answers → skill level |
| GET | `/api/assessment/result` | Latest result |
| GET | `/api/learning-path/` | Personalised topic path |
| POST | `/api/learning-path/set-topic/{id}` | Set current topic |
| GET | `/api/mentor/sessions` | Chat sessions |
| POST | `/api/mentor/sessions` | New session |
| POST | `/api/mentor/sessions/{id}/message` | Send message → AI reply |
| GET | `/api/practice/problems/recommended` | Recommended problems |
| POST | `/api/practice/submissions/{id}` | Submit code → evaluation |
| GET | `/api/progress/` | Full progress summary |
| GET | `/api/admin/users` | All students (admin) |
| GET | `/api/admin/stats` | Platform stats (admin) |

Full interactive docs: `http://localhost:8000/docs`
