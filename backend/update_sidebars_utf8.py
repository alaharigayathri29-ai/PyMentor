import re
from pathlib import Path

sidebar_replacement = """      <nav class="sidebar-nav">
        <div class="nav-section-label">HOME</div>
        <a href="/dashboard.html" class="nav-item" data-page="dashboard">
          <span class="nav-icon">🏠</span> <span>Dashboard</span>
        </a>

        <div class="nav-section-label">LEARNING</div>
        <a href="/learning-path.html" class="nav-item" data-page="courses">
          <span class="nav-icon">📚</span> <span>Courses</span>
        </a>
        <a href="/assessment.html" class="nav-item" data-page="assessment">
          <span class="nav-icon">🎯</span> <span>Skill Certification</span>
        </a>
        <a href="/practice.html" class="nav-item" data-page="practice">
          <span class="nav-icon">💻</span> <span>Code Arena</span>
        </a>
        <a href="/lesson.html" class="nav-item" data-page="lesson">
          <span class="nav-icon">📖</span> <span>Deep Dive Lessons</span>
        </a>

        <div class="nav-section-label">TOOLS</div>
        <a href="/playground.html" class="nav-item" data-page="playground">
          <span class="nav-icon">⚡</span> <span>Playground</span>
        </a>
        <a href="/mentor.html" class="nav-item" data-page="mentor">
          <span class="nav-icon">🤖</span> <span>AI Mentor</span>
        </a>

        <div class="nav-section-label">INSIGHTS</div>
        <a href="/profile.html" class="nav-item" data-page="profile">
          <span class="nav-icon">👤</span> <span>Student Profile</span>
        </a>
        <a href="/progress.html" class="nav-item" data-page="progress">
          <span class="nav-icon">📊</span> <span>My Progress</span>
        </a>

        <div id="nav-admin-section" class="hidden">
          <div class="nav-section-label">ADMIN</div>
          <a href="/admin/dashboard.html" class="nav-item" data-page="admin-dashboard">
            <span class="nav-icon">🛡️</span> <span>Admin Overview</span>
            <span class="nav-badge">Admin</span>
          </a>
          <a href="/admin/students.html" class="nav-item" data-page="admin-students">
            <span class="nav-icon">👥</span> <span>Students</span>
          </a>
        </div>
      </nav>"""

html_files = [
    Path(r"d:\ch work\ai-mentor\frontend\dashboard.html"),
    Path(r"d:\ch work\ai-mentor\frontend\learning-path.html"),
    Path(r"d:\ch work\ai-mentor\frontend\lesson.html"),
    Path(r"d:\ch work\ai-mentor\frontend\practice.html"),
    Path(r"d:\ch work\ai-mentor\frontend\assessment.html"),
    Path(r"d:\ch work\ai-mentor\frontend\profile.html"),
    Path(r"d:\ch work\ai-mentor\frontend\progress.html"),
    Path(r"d:\ch work\ai-mentor\frontend\mentor.html"),
    Path(r"d:\ch work\ai-mentor\frontend\playground.html"),
]

for p in html_files:
    if not p.exists():
        continue
    content = p.read_text(encoding="utf-8")
    
    # Replace the <nav class="sidebar-nav"> ... </nav> block
    updated = re.sub(
        r'<nav class="sidebar-nav">.*?</nav>',
        sidebar_replacement,
        content,
        flags=re.DOTALL
    )
    # Also clean up any lingering '??' or 'Daily Skill Assessment Streak'
    updated = updated.replace("?? Skill Certification", "Skill Certification")
    updated = updated.replace("?? Code Arena", "Code Arena")
    updated = updated.replace("?? Deep Dive Lessons", "Deep Dive Lessons")

    p.write_text(updated, encoding="utf-8")
    print(f"Updated sidebar in: {p.name}")

print("ALL SIDEBARS CLEANED WITH UTF-8!")
