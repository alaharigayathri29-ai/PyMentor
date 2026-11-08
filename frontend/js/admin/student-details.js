/**
 * admin/student-details.js
 * Dedicated Admin Student Dossier Page — Coursify Reference Architecture
 * Inspects a single student's complete records via ?id=X with authentic DB metrics.
 */

import { requireAuth, initLayout, escapeHtml } from '../common.js?v=20261108_v17';
import { adminApi } from '../api.js?v=20261108_v17';
import { showToast } from '../components/toast.js?v=20261108_v17';
import { capitalize, formatDate, formatRelative } from '../utils/formatters.js?v=20261108_v17';
import { renderMarkdown } from '../utils/markdown.js?v=20261108_v17';

let currentStudentId = null;
let currentDossier = null;
let allEnrolledModules = [];

async function init() {
  const user = await requireAuth({ requireAdmin: true });
  if (!user) return;

  initLayout('admin-students', user);

  const urlParams = new URLSearchParams(window.location.search);
  const id = parseInt(urlParams.get('id') || '', 10);

  if (!id) {
    showToast('No student ID provided', 'error');
    const container = document.getElementById('student-details-container');
    if (container) {
      container.innerHTML = `
        <div style="text-align:center;padding:60px 20px;">
          <div style="font-size:36px;margin-bottom:12px;">🔍</div>
          <div style="font-size:16px;font-weight:700;color:var(--text-primary);margin-bottom:8px;">No Student Selected</div>
          <p style="color:var(--text-secondary);font-size:13px;margin-bottom:20px;">Please select a student from the student directory to inspect their profile.</p>
          <a href="/admin/students.html" class="btn btn-primary">Go to Student Directory</a>
        </div>
      `;
    }
    return;
  }

  currentStudentId = id;
  await loadStudentDossier(id);
}

async function loadStudentDossier(id) {
  const container = document.getElementById('student-details-container');
  if (container) {
    container.innerHTML = '<div style="padding:60px;text-align:center;"><div class="spinner"></div></div>';
  }

  try {
    const [detail, submissions, sessions] = await Promise.all([
      adminApi.detail(id),
      adminApi.submissions(id).catch(() => []),
      adminApi.sessions(id).catch(() => []),
    ]);

    currentDossier = { detail, submissions, sessions };
    renderDossier(detail, submissions, sessions);
  } catch (err) {
    showToast(`Failed to load student dossier: ${err.message}`, 'error');
    if (container) {
      container.innerHTML = `
        <div style="text-align:center;padding:60px 20px;">
          <div style="font-size:36px;margin-bottom:12px;color:var(--danger);">⚠️</div>
          <div style="font-size:16px;font-weight:700;color:var(--text-primary);margin-bottom:8px;">Failed to Load Student</div>
          <p style="color:var(--text-secondary);font-size:13px;margin-bottom:20px;">${escapeHtml(err.message)}</p>
          <a href="/admin/students.html" class="btn btn-secondary">← Back to Student Directory</a>
        </div>
      `;
    }
  }
}

function renderDossier(data, subs, sessions) {
  const container = document.getElementById('student-details-container');
  if (!container) return;

  const u = data.profile || data.user || {};
  const summary = data.summary || {};
  const profile = summary.user_profile || {
    id: `STU-${String(u.id || currentStudentId).padStart(3, '0')}`,
    username: u.username || 'Student',
    email: u.email || 'student@example.com',
    enrolled_date: formatDate(u.created_at) || 'Jan 15, 2026',
    is_active: u.is_active !== undefined ? u.is_active : true,
    avatar: (u.username || 'S')[0].toUpperCase(),
  };

  const activity = summary.learning_activity || {
    lifetime_hours: 0,
    lifetime_minutes: 0,
    weekly_breakdown: [],
    top_modules: [],
  };

  const perf = summary.performance || {
    total_score: 0,
    participation_pct: 0,
    quiz_pct: 0,
    practice_pct: 0,
    trend_curve: [],
  };

  allEnrolledModules = summary.enrolled_modules || [];

  // Circumference for semi-circular gauge: PI * 50 = 157.08
  const semiCirc = 157.08;
  const partOffset = semiCirc - (semiCirc * Math.min(100, Math.max(0, perf.participation_pct || 0)) / 100);
  const quizOffset = semiCirc - (semiCirc * Math.min(100, Math.max(0, perf.quiz_pct || 0)) / 100);
  const pracOffset = semiCirc - (semiCirc * Math.min(100, Math.max(0, perf.practice_pct || 0)) / 100);

  // Weekly breakdown columns
  const weekly = activity.weekly_breakdown || [];
  const maxVal = Math.max(1, ...weekly.map(d => (d.submissions || 0) + (d.lessons || 0) + (d.mentor_chats || 0)));
  const stackedBarsHtml = weekly.map(day => {
    const subC = day.submissions || 0;
    const lesC = day.lessons || 0;
    const menC = day.mentor_chats || 0;
    const total = subC + lesC + menC;
    const pinkH = total > 0 ? Math.max(6, Math.round((subC / maxVal) * 55)) : 10;
    const goldH = total > 0 ? Math.max(6, Math.round((lesC / maxVal) * 55)) : 10;
    const blueH = total > 0 ? Math.max(6, Math.round((menC / maxVal) * 45)) : 8;

    return `
      <div class="bar-col" title="${day.day}: ${subC} submissions, ${lesC} lessons, ${menC} inquiries">
        <div class="bar-pill-track">
          <div class="bar-segment pink" style="height: ${pinkH}%;"></div>
          <div class="bar-segment gold" style="height: ${goldH}%;"></div>
          <div class="bar-segment blue" style="height: ${blueH}%;"></div>
        </div>
        <div class="bar-day-label">${escapeHtml(day.day)}</div>
      </div>
    `;
  }).join('');

  // Top 3 activity sub pills
  const topMods = activity.top_modules || [];
  const tintClasses = ['pink-tint', 'gold-tint', 'blue-tint'];
  const subPillsHtml = topMods.slice(0, 3).map((item, idx) => `
    <div class="sub-pill-item ${tintClasses[idx % 3]}">
      <div class="sub-pill-hours">${escapeHtml(item.hours)}</div>
      <div class="sub-pill-title" title="${escapeHtml(item.title)}">${escapeHtml(item.title)}</div>
    </div>
  `).join('') || `
    <div class="sub-pill-item pink-tint">
      <div class="sub-pill-hours">0 <span>Hours</span></div>
      <div class="sub-pill-title">Python Basics</div>
    </div>
    <div class="sub-pill-item gold-tint">
      <div class="sub-pill-hours">0 <span>Hours</span></div>
      <div class="sub-pill-title">Control Flow</div>
    </div>
    <div class="sub-pill-item blue-tint">
      <div class="sub-pill-hours">0 <span>Hours</span></div>
      <div class="sub-pill-title">Functions & OOP</div>
    </div>
  `;

  // Trend points
  const trend = perf.trend_curve || [];
  let trendPoints = [];
  let pathD = 'M 10 50 Q 60 45, 110 35 T 210 30 T 290 20';
  if (trend.length === 6) {
    trendPoints = trend.map((pt, i) => {
      const score = Math.min(100, Math.max(0, pt.score));
      return { x: 10 + (i * 56), y: Math.round(70 - (score * 0.55)) };
    });
    pathD = `M ${trendPoints[0].x} ${trendPoints[0].y} ` +
      `C ${trendPoints[0].x + 25} ${trendPoints[0].y}, ${trendPoints[1].x - 25} ${trendPoints[1].y}, ${trendPoints[1].x} ${trendPoints[1].y} ` +
      `C ${trendPoints[1].x + 25} ${trendPoints[1].y}, ${trendPoints[2].x - 25} ${trendPoints[2].y}, ${trendPoints[2].x} ${trendPoints[2].y} ` +
      `C ${trendPoints[2].x + 25} ${trendPoints[2].y}, ${trendPoints[3].x - 25} ${trendPoints[3].y}, ${trendPoints[3].x} ${trendPoints[3].y} ` +
      `C ${trendPoints[3].x + 25} ${trendPoints[3].y}, ${trendPoints[4].x - 25} ${trendPoints[4].y}, ${trendPoints[4].x} ${trendPoints[4].y} ` +
      `C ${trendPoints[4].x + 25} ${trendPoints[4].y}, ${trendPoints[5].x - 25} ${trendPoints[5].y}, ${trendPoints[5].x} ${trendPoints[5].y}`;
  }

  container.innerHTML = `
    <!-- Top Action Toolbar -->
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:12px;">
      <a href="/admin/students.html" class="btn btn-secondary btn-sm" style="display:inline-flex;gap:6px;align-items:center;border-radius:var(--r-full);padding:6px 16px;">
        <span>←</span> Back to Student Directory
      </a>
      <div style="display:flex;gap:10px;">
        <button class="btn btn-ghost btn-sm" id="btn-toggle-active-status" style="border:1px solid var(--border);border-radius:var(--r-full);padding:6px 14px;color:${u.is_active ? '#DC2626' : '#059669'};">
          ${u.is_active ? 'Deactivate Student Account' : 'Reactivate Student Account'}
        </button>
      </div>
    </div>

    <!-- ── 3-Column Top Monitoring Grid (Matching Reference Image) ──────────── -->
    <div class="dash-monitoring-grid">

      <!-- Column 1: Student Dossier Profile Card -->
      <div class="profile-dossier-card">
        <div class="profile-banner-wrap">
          <div class="profile-avatar-outer">
            <div id="stu-avatar-text">${escapeHtml(profile.avatar)}</div>
          </div>
        </div>

        <div class="profile-info-body">
          <div class="profile-id-pills">
            <span class="pill-id">${escapeHtml(profile.id)}</span>
            <span class="pill-status" style="background-color:${profile.is_active ? '#ECFDF5' : '#FEF2F2'};color:${profile.is_active ? '#059669' : '#DC2626'};">
              ${profile.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>

          <div class="profile-name">${escapeHtml(profile.username)}</div>
          <div class="profile-enrolled">Enrolled on ${escapeHtml(profile.enrolled_date)}</div>

          <div class="profile-action-btns">
            <a href="mailto:${escapeHtml(profile.email)}" class="btn-circle-action" title="Send Email">✉️</a>
            <a href="/admin/analytics.html" class="btn-circle-action" title="Student Analytics">📈</a>
            <button class="btn-chat-action" id="btn-admin-inspect-chats">
              <span>💬</span> Messages (${sessions.length})
            </button>
          </div>

          <!-- Contact Block -->
          <div class="profile-contact-block">
            <div class="profile-contact-title">Contact</div>

            <div class="contact-row">
              <div class="contact-icon-bubble">✉️</div>
              <div style="min-width:0;">
                <div class="contact-label">Email</div>
                <div class="contact-value">${escapeHtml(profile.email)}</div>
              </div>
            </div>

            <div class="contact-row">
              <div class="contact-icon-bubble">🎯</div>
              <div style="min-width:0;">
                <div class="contact-label">Track & Level</div>
                <div class="contact-value">Python Core • ${capitalize(summary.skill_level || 'Beginner')}</div>
              </div>
            </div>

            <div class="contact-row">
              <div class="contact-icon-bubble">🏆</div>
              <div style="min-width:0;">
                <div class="contact-label">Submissions Pass Rate</div>
                <div class="contact-value">${summary.problems_solved || 0} / ${summary.total_submissions || 0} passed (${Math.round(summary.accuracy_pct || 0)}%)</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Column 2: Learning Activity Card with Stacked Bars -->
      <div class="activity-monitoring-card">
        <div class="monitoring-card-header">
          <div class="monitoring-card-title">Learning Activity</div>
          <div style="display:flex;align-items:center;gap:8px;">
            <select class="card-filter-select">
              <option>This Week</option>
              <option>All Time</option>
            </select>
            <span style="color:var(--text-muted);cursor:pointer;font-weight:700;">•••</span>
          </div>
        </div>

        <!-- Headline Time -->
        <div class="activity-headline-time">
          <span class="headline-number">${activity.lifetime_hours}</span>
          <span class="headline-unit">hours</span>
          <span class="headline-number" style="margin-left:8px;">${activity.lifetime_minutes}</span>
          <span class="headline-unit">minutes</span>
        </div>

        <!-- Stacked Bar Chart (Mon - Sun) -->
        <div class="stacked-chart-container">
          <div class="stacked-bars-row">
            ${stackedBarsHtml}
          </div>
        </div>

        <!-- 3 Sub Pills -->
        <div class="activity-sub-pills">
          ${subPillsHtml}
        </div>
      </div>

      <!-- Column 3: Performance Card with Gauge & Trend Line -->
      <div class="performance-monitoring-card">
        <div class="monitoring-card-header">
          <div class="monitoring-card-title">Performance</div>
          <select class="card-filter-select">
            <option>Last 6 Months</option>
            <option>All Time</option>
          </select>
        </div>

        <!-- Semi-Circular Gauge -->
        <div class="gauge-section">
          <div class="gauge-svg-wrap">
            <svg width="140" height="85" viewBox="0 0 140 85">
              <path d="M 20 75 A 50 50 0 0 1 120 75" fill="none" stroke="#F1F5F9" stroke-width="12" stroke-linecap="round" />
              <path d="M 20 75 A 50 50 0 0 1 120 75" fill="none" stroke="#F472B6" stroke-width="12" stroke-linecap="round" stroke-dasharray="157.08" stroke-dashoffset="${partOffset}" />
              <path d="M 20 75 A 50 50 0 0 1 120 75" fill="none" stroke="#FBBF24" stroke-width="12" stroke-linecap="round" stroke-dasharray="157.08" stroke-dashoffset="${quizOffset}" />
              <path d="M 20 75 A 50 50 0 0 1 120 75" fill="none" stroke="#93C5FD" stroke-width="12" stroke-linecap="round" stroke-dasharray="157.08" stroke-dashoffset="${pracOffset}" />
            </svg>
            <div class="gauge-center-text">
              <div class="gauge-score-label">Total Score</div>
              <div class="gauge-score-val">${perf.total_score}%</div>
            </div>
          </div>

          <div class="gauge-legend-list">
            <div class="legend-item">
              <div class="legend-dot-label">
                <span class="legend-color-dot" style="background-color:#F472B6;"></span>
                <span>Participation</span>
              </div>
              <div class="legend-val">${perf.participation_pct}%</div>
            </div>
            <div class="legend-item">
              <div class="legend-dot-label">
                <span class="legend-color-dot" style="background-color:#FBBF24;"></span>
                <span>Quiz</span>
              </div>
              <div class="legend-val">${perf.quiz_pct}%</div>
            </div>
            <div class="legend-item">
              <div class="legend-dot-label">
                <span class="legend-color-dot" style="background-color:#93C5FD;"></span>
                <span>Practice</span>
              </div>
              <div class="legend-val">${perf.practice_pct}%</div>
            </div>
          </div>
        </div>

        <!-- Trend Line -->
        <div class="performance-trend-wrap">
          <svg class="trend-svg" viewBox="0 0 300 80">
            <defs>
              <linearGradient id="adminTrendGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#F472B6" stop-opacity="0.25"/>
                <stop offset="100%" stop-color="#F472B6" stop-opacity="0.0"/>
              </linearGradient>
            </defs>
            <path d="${pathD} L 290 75 L 10 75 Z" fill="url(#adminTrendGrad)" />
            <path d="${pathD}" fill="none" stroke="#F472B6" stroke-width="2.5" stroke-linecap="round"/>
            ${trendPoints.map(pt => `<circle cx="${pt.x}" cy="${pt.y}" r="3.5" fill="#FFFFFF" stroke="#F472B6" stroke-width="2"/>`).join('')}
          </svg>
          <div class="trend-labels-row">
            <span>Jan</span>
            <span>Feb</span>
            <span>Mar</span>
            <span>Apr</span>
            <span>May</span>
            <span>Jun</span>
          </div>
        </div>

        <!-- Motivational Quote -->
        <div class="motivational-insight-box">
          <span>💡</span>
          <div>Success is the sum of small efforts, repeated day in and day out. Active practice drives mastery! 🎯</div>
        </div>
      </div>

    </div>

    <!-- ── Bottom Section: Enrolled Courses & Modules ───────────────────────── -->
    <div class="enrolled-courses-card" style="margin-bottom:24px;">
      <div class="courses-card-header">
        <div style="font-size:18px;font-weight:800;color:var(--text-primary);">Enrolled Courses</div>

        <div class="courses-header-controls">
          <div class="course-search-field">
            <span style="color:var(--text-muted);">🔍</span>
            <input type="text" id="admin-course-search" placeholder="Search course, module, etc">
          </div>

          <select class="card-filter-select" id="admin-course-filter">
            <option value="all">All Status</option>
            <option value="ongoing">Ongoing</option>
            <option value="completed">Completed</option>
            <option value="available">Available</option>
          </select>
        </div>
      </div>

      <div class="module-rows-list" id="admin-enrolled-modules-container">
        ${renderModulesRows(allEnrolledModules)}
      </div>
    </div>

    <!-- ── Submissions & AI Inquiries Tab Section ───────────────────────────── -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
      <!-- Recent Submissions -->
      <div class="enrolled-courses-card">
        <div style="font-size:16px;font-weight:700;margin-bottom:16px;color:var(--text-primary);">Recent Submissions (${subs.length})</div>
        <div style="max-height:360px;overflow-y:auto;display:flex;flex-direction:column;gap:8px;">
          ${subs.length > 0 ? subs.slice(0, 10).map(s => `
            <div style="padding:10px 14px;border:1px solid #F1F5F9;border-radius:10px;display:flex;justify-content:space-between;align-items:center;">
              <div>
                <div style="font-size:13px;font-weight:700;color:var(--text-primary);">${escapeHtml(s.problem_title || 'Coding Problem')}</div>
                <div style="font-size:11px;color:var(--text-muted);">${formatRelative(s.submitted_at)}</div>
              </div>
              <span class="badge ${s.score >= 70 ? 'badge-green' : 'badge-red'}" style="font-size:11px;">
                ${s.passed_tests}/${s.total_tests} (${Math.round(s.score)}%)
              </span>
            </div>
          `).join('') : '<div style="color:var(--text-muted);font-size:13px;padding:12px;">No submissions yet.</div>'}
        </div>
      </div>

      <!-- AI Mentor Inquiries -->
      <div class="enrolled-courses-card">
        <div style="font-size:16px;font-weight:700;margin-bottom:16px;color:var(--text-primary);display:flex;justify-content:space-between;align-items:center;">
          <span>AI Mentor Sessions (${sessions.length})</span>
          ${sessions.length > 0 ? `<button class="btn btn-ghost btn-sm" id="btn-view-all-chats" style="font-size:12px;">Inspect All →</button>` : ''}
        </div>
        <div style="max-height:360px;overflow-y:auto;display:flex;flex-direction:column;gap:8px;">
          ${sessions.length > 0 ? sessions.slice(0, 10).map((s, idx) => `
            <div class="admin-session-item" data-session-idx="${idx}" style="padding:10px 14px;border:1px solid #F1F5F9;border-radius:10px;display:flex;justify-content:space-between;align-items:center;cursor:pointer;transition:all 0.15s;" onmouseover="this.style.borderColor='var(--primary)';this.style.background='#FFFDF8';" onmouseout="this.style.borderColor='#F1F5F9';this.style.background='white';">
              <div style="min-width:0;flex:1;">
                <div style="font-size:13px;font-weight:700;color:var(--text-primary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${escapeHtml(s.title || s.topic || 'Python Inquiry')}</div>
                <div style="font-size:11px;color:var(--text-muted);">${formatRelative(s.created_at)} • ${(s.messages ? s.messages.length : (s.message_count || 1))} messages</div>
              </div>
              <div style="display:flex;align-items:center;gap:6px;">
                <span class="badge badge-blue" style="font-size:11px;">Completed</span>
                <span style="font-size:12px;color:var(--primary);font-weight:600;">View 💬</span>
              </div>
            </div>
          `).join('') : '<div style="color:var(--text-muted);font-size:13px;padding:12px;">No AI mentor sessions yet.</div>'}
        </div>
      </div>
    </div>
  `;

  // Attach Chat Inspection Events
  const openChatForIdx = (idx = 0) => {
    if (!sessions || sessions.length === 0) {
      showToast('This student has not started any AI mentor chats yet.', 'info');
      return;
    }
    openStudentChatModal(idx, sessions, profile.username);
  };

  const inspectChatsBtn = document.getElementById('btn-admin-inspect-chats');
  if (inspectChatsBtn) {
    inspectChatsBtn.addEventListener('click', () => openChatForIdx(0));
  }

  const viewAllBtn = document.getElementById('btn-view-all-chats');
  if (viewAllBtn) {
    viewAllBtn.addEventListener('click', () => openChatForIdx(0));
  }

  document.querySelectorAll('.admin-session-item').forEach(el => {
    el.addEventListener('click', () => {
      const idx = parseInt(el.getAttribute('data-session-idx'), 10);
      openChatForIdx(idx);
    });
  });

  // Attach Toggle Status Event
  const toggleBtn = document.getElementById('btn-toggle-active-status');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', async () => {
      try {
        const nextState = !u.is_active;
        await adminApi.toggleActive(currentStudentId, nextState);
        showToast(`Student account ${nextState ? 'activated' : 'deactivated'} successfully`, 'success');
        await loadStudentDossier(currentStudentId);
      } catch (err) {
        showToast(`Failed to update status: ${err.message}`, 'error');
      }
    });
  }

  // Attach search and filter events
  const searchInput = document.getElementById('admin-course-search');
  const statusFilter = document.getElementById('admin-course-filter');
  const onFilter = () => {
    const q = (searchInput?.value || '').toLowerCase().trim();
    const st = statusFilter?.value || 'all';
    const rows = document.querySelectorAll('.course-module-row');
    rows.forEach(r => {
      const title = r.getAttribute('data-title') || '';
      const status = r.getAttribute('data-status') || '';
      const mQ = !q || title.includes(q);
      const mS = st === 'all' || status === st;
      r.style.display = (mQ && mS) ? 'flex' : 'none';
    });
  };
  if (searchInput) searchInput.addEventListener('input', onFilter);
  if (statusFilter) statusFilter.addEventListener('change', onFilter);
}

function renderModulesRows(modules) {
  if (!modules || modules.length === 0) {
    return '<div style="padding:24px;text-align:center;color:var(--text-muted);font-size:13px;">No curriculum modules assigned.</div>';
  }

  return modules.map(m => {
    const statusLower = (m.status || 'available').toLowerCase();
    const statusClass = statusLower.includes('ongoing') ? 'ongoing' : (statusLower.includes('completed') ? 'completed' : 'available');
    const badgeText = capitalize(m.status || 'Available');
    const progress = Math.min(100, Math.max(0, Math.round(m.progress_pct || 0)));
    const avgScore = Math.round(m.average_score || 0);

    const miniCirc = 56.55;
    const miniOffset = miniCirc - (miniCirc * progress / 100);

    return `
      <div class="course-module-row" data-title="${escapeHtml(m.title.toLowerCase())}" data-status="${statusClass}">
        <div class="course-row-left">
          <div class="course-module-icon">${escapeHtml(m.icon || '🐍')}</div>
          <div class="course-module-info">
            <div class="course-module-title">${escapeHtml(m.title)}</div>
            <div class="course-module-meta">${escapeHtml(m.category || 'Core Python')}</div>
          </div>
        </div>

        <div class="course-row-stats">
          <div class="course-lessons-stat" title="Lessons & estimated time">
            <span>▶ ${m.topic_count || 1}</span>
            <span>•</span>
            <span>⏱ ${m.estimated_hours || 3}h</span>
          </div>

          <div class="course-progress-pill" title="Module Mastery Progress">
            <svg class="mini-circle-pct" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="9" fill="none" stroke="#F1F5F9" stroke-width="2.5" />
              <circle cx="12" cy="12" r="9" fill="none" stroke="#EC4899" stroke-width="2.5"
                stroke-dasharray="56.55" stroke-dashoffset="${miniOffset}"
                transform="rotate(-90 12 12)" stroke-linecap="round" />
            </svg>
            <span>${progress}%</span>
          </div>

          <span class="status-badge-coursify ${statusClass}">
            ${badgeText}
          </span>

          <div class="course-score-badge">
            ${avgScore}<span>/100</span>
          </div>

          <div class="certificate-badge ${m.has_certificate ? 'earned' : ''}">
            <span>${m.has_certificate ? '🏆 Certificate' : 'Certificate: None'}</span>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

function openStudentChatModal(activeIdx, sessions, username) {
  // Remove existing modal if any
  document.getElementById('admin-chat-inspect-modal')?.remove();

  let currentIdx = Math.max(0, Math.min(activeIdx, sessions.length - 1));

  const modalOverlay = document.createElement('div');
  modalOverlay.id = 'admin-chat-inspect-modal';
  modalOverlay.className = 'modal-overlay';
  modalOverlay.style.cssText = `
    position: fixed; inset: 0; background: rgba(15, 23, 42, 0.65);
    backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);
    z-index: 99999; display: flex; align-items: center; justify-content: center;
    padding: 20px; animation: modalFadeIn 0.2s ease-out;
  `;

  const renderModalContent = () => {
    const sess = sessions[currentIdx] || { title: 'No Conversation', messages: [] };
    const msgs = sess.messages || [];

    modalOverlay.innerHTML = `
      <div class="modal-content-card" style="
        background: #FFFFFF;
        border: 1.5px solid rgba(200, 160, 100, 0.3);
        border-radius: 16px;
        width: 100%;
        max-width: 760px;
        max-height: 85vh;
        display: flex;
        flex-direction: column;
        box-shadow: 0 24px 64px rgba(15, 23, 42, 0.25);
        overflow: hidden;
      ">
        <!-- Header -->
        <div style="padding: 16px 22px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; background: #FFFDF9;">
          <div>
            <div style="display: flex; align-items: center; gap: 8px;">
              <span style="font-size: 18px;">🤖</span>
              <h3 style="font-size: 16px; font-weight: 800; color: #1C0E04; margin: 0;">AI Mentor Chat: ${escapeHtml(username)}</h3>
              <span class="badge badge-purple" style="font-size: 11px;">Session ${currentIdx + 1} of ${sessions.length}</span>
            </div>
            <div style="font-size: 12px; color: var(--text-muted); margin-top: 3px;">
              ${escapeHtml(sess.title || 'Untitled Session')} • Created ${formatDate(sess.created_at)} • ${msgs.length} messages
            </div>
          </div>
          <button id="btn-close-chat-modal" style="background: transparent; border: none; font-size: 20px; color: var(--text-secondary); cursor: pointer; padding: 4px 8px; border-radius: 6px;">✕</button>
        </div>

        <!-- Session Selector Tabs if multiple sessions -->
        ${sessions.length > 1 ? `
          <div style="display: flex; gap: 6px; padding: 10px 18px; background: #F8FAFC; border-bottom: 1px solid var(--border); overflow-x: auto;">
            ${sessions.map((s, idx) => `
              <button class="chat-tab-btn" data-idx="${idx}" style="
                padding: 6px 12px; border-radius: 8px; font-size: 12px; font-weight: 600; cursor: pointer; white-space: nowrap;
                border: 1px solid ${idx === currentIdx ? 'var(--primary)' : 'var(--border)'};
                background: ${idx === currentIdx ? 'var(--primary-light)' : '#FFFFFF'};
                color: ${idx === currentIdx ? 'var(--primary)' : 'var(--text-secondary)'};
              ">
                💬 ${escapeHtml(s.title || `Chat ${idx + 1}`)} (${s.messages ? s.messages.length : (s.message_count || 0)})
              </button>
            `).join('')}
          </div>
        ` : ''}

        <!-- Messages Container -->
        <div style="flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 14px; background: #FAFAFA;">
          ${msgs.length === 0 ? `
            <div style="text-align: center; padding: 40px; color: var(--text-muted); font-size: 13px;">
              No messages found in this session.
            </div>
          ` : msgs.map(m => {
            const isUser = m.role === 'user';
            return `
              <div style="display: flex; gap: 10px; align-items: flex-start; ${isUser ? 'flex-direction: row-reverse;' : ''}">
                <div style="width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0; background: ${isUser ? '#3B82F6' : '#10B981'}; color: white; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
                  ${isUser ? '👤' : '🤖'}
                </div>
                <div style="
                  max-width: 80%; padding: 12px 16px; border-radius: 12px; font-size: 13px; line-height: 1.6;
                  background: ${isUser ? '#EFF6FF' : '#FFFFFF'};
                  border: 1px solid ${isUser ? '#BFDBFE' : '#E2E8F0'};
                  color: #0F172A;
                  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
                ">
                  <div style="font-size: 11px; font-weight: 700; color: ${isUser ? '#2563EB' : '#059669'}; margin-bottom: 4px;">
                    ${isUser ? escapeHtml(username) : 'PyMentor AI'}
                  </div>
                  <div class="markdown-body" style="font-size: 13px;">
                    ${isUser ? escapeHtml(m.content) : renderMarkdown(m.content)}
                  </div>
                  <div style="font-size: 10px; color: var(--text-muted); margin-top: 6px; text-align: right;">
                    ${m.created_at ? formatRelative(m.created_at) : ''}
                  </div>
                </div>
              </div>
            `;
          }).join('')}
        </div>

        <!-- Footer -->
        <div style="padding: 12px 22px; border-top: 1px solid var(--border); background: #FFFFFF; display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 12px; color: var(--text-muted);">
            Student User ID: <strong>#${currentStudentId}</strong>
          </span>
          <button id="btn-close-chat-bottom" class="btn btn-secondary btn-sm">Close</button>
        </div>
      </div>
    `;

    // Bind Close Buttons
    modalOverlay.querySelector('#btn-close-chat-modal')?.addEventListener('click', () => modalOverlay.remove());
    modalOverlay.querySelector('#btn-close-chat-bottom')?.addEventListener('click', () => modalOverlay.remove());

    // Bind Session Tab Switchers
    modalOverlay.querySelectorAll('.chat-tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        currentIdx = parseInt(btn.getAttribute('data-idx'), 10);
        renderModalContent();
      });
    });
  };

  renderModalContent();

  modalOverlay.addEventListener('click', (e) => {
    if (e.target === modalOverlay) modalOverlay.remove();
  });

  document.body.appendChild(modalOverlay);
}

init();
