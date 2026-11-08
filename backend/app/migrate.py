"""
Database migration script to add curriculum and progression columns
without breaking existing data in SQLite.
"""
import sqlite3
import os

def migrate_database(db_path: str):
    if not os.path.exists(db_path):
        print(f"[MIGRATE] DB file not found at {db_path}, skipping migration.")
        return

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Helper to get column names for a table
    def get_columns(table_name):
        c.execute(f"PRAGMA table_info({table_name})")
        return [row[1] for row in c.fetchall()]

    # 1. Update topics table
    topic_cols = get_columns("topics")
    new_topic_cols = [
        ("module_number", "INTEGER DEFAULT 1"),
        ("module_name", "VARCHAR(100) DEFAULT 'Python Fundamentals'"),
        ("subtopics", "JSON DEFAULT '[]'"),
        ("learning_objectives", "JSON DEFAULT '[]'"),
        ("lesson_content", "JSON DEFAULT '{}'"),
        ("prerequisites", "JSON DEFAULT '[]'"),
    ]
    for col_name, col_type in new_topic_cols:
        if col_name not in topic_cols:
            print(f"[MIGRATE] Adding column topics.{col_name}")
            c.execute(f"ALTER TABLE topics ADD COLUMN {col_name} {col_type}")

    # 2. Update student_knowledge table
    sk_cols = get_columns("student_knowledge")
    new_sk_cols = [
        ("completed_lessons", "JSON DEFAULT '[]'"),
        ("lesson_completed", "BOOLEAN DEFAULT 0"),
        ("quiz_completed", "BOOLEAN DEFAULT 0"),
        ("practice_completed", "BOOLEAN DEFAULT 0"),
    ]
    for col_name, col_type in new_sk_cols:
        if col_name not in sk_cols:
            print(f"[MIGRATE] Adding column student_knowledge.{col_name}")
            c.execute(f"ALTER TABLE student_knowledge ADD COLUMN {col_name} {col_type}")

    # 3. Update practice_problems table
    pp_cols = get_columns("practice_problems")
    if "constraints" not in pp_cols:
        print("[MIGRATE] Adding column practice_problems.constraints")
        c.execute("ALTER TABLE practice_problems ADD COLUMN constraints TEXT DEFAULT ''")

    conn.commit()
    conn.close()
    print("[MIGRATE] Database migration successfully completed.")

if __name__ == "__main__":
    import sys
    db_file = sys.argv[1] if len(sys.argv) > 1 else "D:/ch work/ai-mentor/backend/ai_mentor.db"
    migrate_database(db_file)

