-- ==============================================================================
-- PyMentor Polyglot Platform — Unified PostgreSQL + pgvector Supabase Schema
-- Architecture: 4 Systems Courses (Python, C, Modern C++, Enterprise Java)
-- Compatibility: Supabase / PostgreSQL 15+ / Render PostgreSQL
-- ==============================================================================

-- 1. Enable required PostgreSQL Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector"; -- pgvector for AI semantic search & RAG

-- 2. ENUM Types
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('student', 'admin', 'instructor');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE course_track AS ENUM ('python', 'c', 'cpp', 'java');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE topic_status AS ENUM ('locked', 'available', 'in_progress', 'completed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE difficulty_level AS ENUM ('beginner', 'intermediate', 'advanced');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 3. Core Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(150),
    role user_role DEFAULT 'student' NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    avatar_url VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 4. User Academic Profiles & Vitals
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    college_name VARCHAR(200) DEFAULT 'QIS College of Engineering & Technology',
    branch VARCHAR(100) DEFAULT 'Computer Science & Engineering',
    academic_year VARCHAR(50) DEFAULT '2026-2027',
    primary_track course_track DEFAULT 'python',
    skill_level difficulty_level DEFAULT 'intermediate',
    xp INTEGER DEFAULT 0 NOT NULL,
    streak_days INTEGER DEFAULT 0 NOT NULL,
    last_active_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 5. Curriculum Topics Matrix (All 4 Courses)
CREATE TABLE IF NOT EXISTS topics (
    id SERIAL PRIMARY KEY,
    course course_track NOT NULL,
    module_number INTEGER NOT NULL,
    module_name VARCHAR(150) NOT NULL,
    slug VARCHAR(120) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    order_index INTEGER DEFAULT 1 NOT NULL,
    difficulty difficulty_level DEFAULT 'beginner' NOT NULL,
    icon VARCHAR(10) DEFAULT '📘',
    prerequisites INTEGER[] DEFAULT '{}',
    subtopics TEXT[] DEFAULT '{}',
    learning_objectives TEXT[] DEFAULT '{}',
    lesson_content JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 6. Student Knowledge & Mastery Records
CREATE TABLE IF NOT EXISTS student_knowledge (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    course course_track NOT NULL,
    status topic_status DEFAULT 'available' NOT NULL,
    mastery_score INTEGER DEFAULT 0 NOT NULL CHECK (mastery_score >= 0 AND mastery_score <= 100),
    stars_earned INTEGER DEFAULT 0 NOT NULL CHECK (stars_earned >= 0 AND stars_earned <= 3),
    lesson_completed BOOLEAN DEFAULT FALSE NOT NULL,
    last_practiced_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT unique_user_topic UNIQUE (user_id, topic_id)
);

-- 7. Practice Problems (50 per topic, 1,800+ total)
CREATE TABLE IF NOT EXISTS practice_problems (
    id SERIAL PRIMARY KEY,
    topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    course course_track NOT NULL,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    difficulty difficulty_level DEFAULT 'easy' NOT NULL,
    description TEXT NOT NULL,
    input_format TEXT,
    output_format TEXT,
    constraints TEXT,
    starter_code TEXT NOT NULL,
    solution_code TEXT,
    test_cases JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 8. Code Submissions Ledger
CREATE TABLE IF NOT EXISTS practice_submissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    problem_id INTEGER NOT NULL REFERENCES practice_problems(id) ON DELETE CASCADE,
    course course_track NOT NULL,
    submitted_code TEXT NOT NULL,
    status VARCHAR(50) NOT NULL, -- 'passed', 'failed', 'runtime_error'
    passed_tests INTEGER DEFAULT 0 NOT NULL,
    total_tests INTEGER DEFAULT 0 NOT NULL,
    score NUMERIC(5, 2) DEFAULT 0.00 NOT NULL,
    runtime_ms INTEGER,
    memory_kb INTEGER,
    submitted_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 9. AI Mentor Chat Sessions & Conversations
CREATE TABLE IF NOT EXISTS mentor_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) DEFAULT 'Polyglot Engineering Discussion',
    course course_track DEFAULT 'python',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS mentor_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES mentor_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    programming_language VARCHAR(30) DEFAULT 'python',
    spoken_language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 10. Proctoring & Skill Certification Assessments
CREATE TABLE IF NOT EXISTS assessment_attempts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course course_track NOT NULL,
    score NUMERIC(5, 2) NOT NULL,
    passed BOOLEAN DEFAULT FALSE NOT NULL,
    total_questions INTEGER DEFAULT 6 NOT NULL,
    correct_count INTEGER DEFAULT 0 NOT NULL,
    tab_switches INTEGER DEFAULT 0 NOT NULL,
    proctoring_verified BOOLEAN DEFAULT TRUE NOT NULL,
    webcam_verified BOOLEAN DEFAULT TRUE NOT NULL,
    integrity_flags JSONB DEFAULT '[]'::jsonb,
    answers_payload JSONB DEFAULT '{}'::jsonb,
    completed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 11. pgvector: AI Knowledge Base Embeddings for RAG (768-dim for Gemini text-embedding-004)
CREATE TABLE IF NOT EXISTS topic_knowledge_embeddings (
    id SERIAL PRIMARY KEY,
    topic_id INTEGER REFERENCES topics(id) ON DELETE CASCADE,
    course course_track NOT NULL,
    title VARCHAR(255) NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(768) NOT NULL, -- Google Gemini text-embedding-004
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 12. High-Performance HNSW & B-Tree Indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_topics_course ON topics(course);
CREATE INDEX IF NOT EXISTS idx_topics_slug ON topics(slug);
CREATE INDEX IF NOT EXISTS idx_student_knowledge_user ON student_knowledge(user_id);
CREATE INDEX IF NOT EXISTS idx_student_knowledge_course ON student_knowledge(course);
CREATE INDEX IF NOT EXISTS idx_practice_problems_topic ON practice_problems(topic_id);
CREATE INDEX IF NOT EXISTS idx_practice_problems_course ON practice_problems(course);
CREATE INDEX IF NOT EXISTS idx_practice_submissions_user ON practice_submissions(user_id);
CREATE INDEX IF NOT EXISTS idx_assessment_attempts_user ON assessment_attempts(user_id);

-- HNSW Vector Index for Instant Cosine Distance Similarity Matching
CREATE INDEX IF NOT EXISTS idx_topic_knowledge_embeddings_hnsw 
ON topic_knowledge_embeddings 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 13. Semantic Vector Search SQL Function
CREATE OR REPLACE FUNCTION match_curriculum_knowledge(
    query_embedding vector(768),
    match_threshold float,
    match_count int,
    filter_course course_track DEFAULT NULL
)
RETURNS TABLE (
    id int,
    topic_id int,
    course course_track,
    title varchar,
    chunk_text text,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.topic_id,
        e.course,
        e.title,
        e.chunk_text,
        1 - (e.embedding <=> query_embedding) AS similarity
    FROM topic_knowledge_embeddings e
    WHERE (filter_course IS NULL OR e.course = filter_course)
      AND 1 - (e.embedding <=> query_embedding) > match_threshold
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- 14. Row Level Security (RLS) Configurations
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_knowledge ENABLE ROW LEVEL SECURITY;
ALTER TABLE practice_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE mentor_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE mentor_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessment_attempts ENABLE ROW LEVEL SECURITY;

-- Default permissive read-all for public topics & practice problems
ALTER TABLE topics ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public can view topics" ON topics FOR SELECT USING (true);

ALTER TABLE practice_problems ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public can view problems" ON practice_problems FOR SELECT USING (true);

ALTER TABLE topic_knowledge_embeddings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public can query vector knowledge" ON topic_knowledge_embeddings FOR SELECT USING (true);

