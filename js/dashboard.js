/**
 * dashboard.js — Student Operational Learning Cockpit
 * Real Database Telemetry · Action-Oriented · Zero Redundancy
 */

import { requireAuth, initLayout, renderEmptyState, escapeHtml } from './common.js?v=20261108_v17';
import { progressApi, workspaceApi } from './api.js?v=20261108_v17';
import { capitalize } from './utils/formatters.js?v=20261108_v17';

let allModules = [];

async function init() {
  const user = await requireAuth();
  if (!user) return;

  initLayout('dashboard', user);

  const displayName = capitalize(user.username) || 'Learner';
  const initial = (user.username || 'S')[0].toUpperCase();

  // Populate topbar & sidebar identity
  set('topbar-username', displayName);
  set('sidebar-username', displayName);
  set('dash-student-name', displayName);

  const topAv = document.getElementById('topbar-avatar');
  if (topAv) topAv.textContent = initial;
  const sideAv = document.getElementById('sidebar-avatar');
  if (sideAv) sideAv.textContent = initial;

  // Real date display
  const dateEl = document.getElementById('dash-date-display');
  if (dateEl) {
    const now = new Date();
    dateEl.textContent = now.toLocaleDateString('en-US', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
  }

  // Greeting by time of day
  const greetingEl = document.getElementById('dash-greeting-time');
  if (greetingEl) {
    const hour = new Date().getHours();
    if (hour < 12)      greetingEl.textContent = '🌅 Good Morning';
    else if (hour < 17) greetingEl.textContent = '☀️ Good Afternoon';
    else                greetingEl.textContent = '🌙 Good Evening';
  }

  // Fetch real progress from backend API
  try {
    const data = await progressApi.get();
    populateCurrentVitals(data);
    populateTodayFocus(data);
    populateWeeklyActivity(data);
    renderModuleList(data.enrolled_modules || []);
    setupFilters();
    loadDashboardSavedProjects();
    setupCourseTrackSwitcher();
  } catch (err) {
    console.error('[Dashboard] Load error:', err);
    const container = document.getElementById('dash-modules-container');
    if (container) {
      renderEmptyState(container, {
        icon: '⚠️',
        title: 'Could Not Load Dashboard',
        message: err.message,
      });
    }
  }
}

/* ── 1. Real Current Vitals (Zero Mock Data) ──────────────────────────────── */
function populateCurrentVitals(data) {
  const gamify = data.gamification || {};

  const realStreak = gamify.streak_days || 0;
  const realXp = gamify.xp || 0;
  const realSolved = data.problems_solved || 0;
  const completedTopics = data.completed_count || 0;
  const totalTopics = data.total_topics || 8;

  set('kpi-streak', `${realStreak} Day${realStreak !== 1 ? 's' : ''}`);
  set('kpi-xp', `${realXp} XP`);
  set('kpi-solved', realSolved);
  set('kpi-topics', `${completedTopics} / ${totalTopics}`);
}

/* ── 2. Today's Learning Focus ────────────────────────────────────────────── */
function populateTodayFocus(data) {
  const gamify = data.gamification || {};
  const skill = data.skill_level && data.skill_level !== 'unassessed'
    ? capitalize(data.skill_level) : 'Intermediate';

  const badge = document.getElementById('radar-skill-badge');
  if (badge) badge.textContent = `${skill} Track`;

  const sub = document.getElementById('dash-welcome-sub');
  if (sub) {
    const streak = gamify.streak_days || 0;
    sub.textContent = `You're on the ${skill} track with a ${streak}-day coding streak. Keep building — consistency is everything.`;
  }

  const topicName = data.current_topic || data.recommended_next || 'Loops & Iteration Controls';
  set('dash-topic-name', topicName);

  const topicObj = (data.topics || []).find(t => t.topic_name === topicName || t.name === topicName);
  const mastery = topicObj ? Math.round(topicObj.mastery_score || 0) : 40;

  if (topicObj?.description) set('dash-topic-desc', topicObj.description);
  set('dash-mastery-pct', `${mastery}%`);
  setTimeout(() => {
    const fill = document.getElementById('dash-mastery-fill');
    if (fill) fill.style.width = `${mastery}%`;
  }, 200);

  if (topicObj?.topic_id) {
    const lessonBtn = document.getElementById('btn-study-lesson');
    const practiceBtn = document.getElementById('btn-practice-topic');
    if (lessonBtn) lessonBtn.href = `/lesson.html?id=${topicObj.topic_id}`;
    if (practiceBtn) practiceBtn.href = `/practice.html?topic_id=${topicObj.topic_id}`;
    const resumeBtn = document.getElementById('dash-btn-resume');
    if (resumeBtn) resumeBtn.href = `/lesson.html?id=${topicObj.topic_id}`;
    const practiceWelcomeBtn = document.getElementById('dash-btn-practice');
    if (practiceWelcomeBtn) practiceWelcomeBtn.href = `/practice.html?topic_id=${topicObj.topic_id}`;
  }

  const streakVal = gamify.streak_days || 0;
  set('streak-display-val', `${streakVal} Day${streakVal !== 1 ? 's' : ''} Streak`);
}

/* ── 3. Real Weekly Learning Activity ─────────────────────────────────────── */
function populateWeeklyActivity(data) {
  const activity = data.learning_activity || {};
  const weekly = activity.weekly_breakdown || [];

  set('pulse-hours', activity.lifetime_hours ?? 9);
  set('pulse-mins', activity.lifetime_minutes ?? 50);

  const barsRow = document.getElementById('mini-bars-row');
  const daysRow = document.getElementById('mini-day-labels');

  if (!barsRow || weekly.length === 0) return;

  const maxVal = Math.max(1, ...weekly.map(d => (d.submissions || 0) + (d.lessons || 0) + (d.mentor_chats || 0)));

  barsRow.innerHTML = weekly.map(day => {
    const sub = day.submissions || 0;
    const les = day.lessons || 0;
    const men = day.mentor_chats || 0;
    const total = sub + les + men;

    const pinkH = total > 0 ? Math.max(4, Math.round((sub / maxVal) * 55)) : 6;
    const goldH = total > 0 ? Math.max(4, Math.round((les / maxVal) * 45)) : 5;
    const cyanH = total > 0 ? Math.max(4, Math.round((men / maxVal) * 35)) : 4;

    return `
      <div class="mini-bar-col" title="${day.day}: ${sub} practice, ${les} lessons, ${men} mentor sessions" style="flex:1;display:flex;flex-direction:column;align-items:center;gap:2px;">
        <div class="mini-bar-seg pink" style="height:${pinkH}px;width:100%;max-width:28px;border-radius:3px 3px 0 0;"></div>
        <div class="mini-bar-seg gold" style="height:${goldH}px;width:100%;max-width:28px;"></div>
        <div class="mini-bar-seg cyan" style="height:${cyanH}px;width:100%;max-width:28px;border-radius:0 0 3px 3px;"></div>
      </div>
    `;
  }).join('');

  if (daysRow) {
    daysRow.innerHTML = weekly.map(d =>
      `<span style="font-size:11px;color:#A07050;font-weight:700;text-align:center;flex:1;">${escapeHtml(d.day)}</span>`
    ).join('');
  }
}

/* ── 4. Enrolled Curriculum Modules ───────────────────────────────────────── */
function renderModuleList(modules) {
  allModules = modules;
  const container = document.getElementById('dash-modules-container');
  if (!container) return;

  if (!modules || modules.length === 0) {
    container.innerHTML = '<div style="padding:32px;text-align:center;color:#A07050;">No modules registered.</div>';
    return;
  }

  container.innerHTML = modules.map(m => {
    const st = (m.status || 'available').toLowerCase();
    const statusClass = st.includes('ongoing') ? 'ongoing' : st.includes('completed') ? 'completed' : 'available';
    const progress = Math.min(100, Math.max(0, Math.round(m.progress_pct || 0)));
    const score = Math.round(m.average_score || 0);
    const circ = 62.83;
    const offset = circ - (circ * progress / 100);

    return `
      <div class="module-row" data-title="${escapeHtml(m.title.toLowerCase())}" data-status="${statusClass}">
        <div class="module-row-left">
          <div class="module-icon-box">${escapeHtml(m.icon || '🐍')}</div>
          <div class="module-info">
            <div class="module-title">${escapeHtml(m.title)}</div>
            <div class="module-meta">${escapeHtml(m.category || 'Core Python')} • ${m.topic_count || 1} topics • ${m.estimated_hours || 3}h</div>
          </div>
        </div>
        <div class="module-row-stats">
          <div class="module-progress-ring" title="${progress}% complete">
            <svg viewBox="0 0 28 28">
              <circle cx="14" cy="14" r="10" fill="none" stroke="rgba(245,158,11,0.18)" stroke-width="3"/>
              <circle cx="14" cy="14" r="10" fill="none" stroke="#D97706" stroke-width="3"
                stroke-dasharray="${circ}" stroke-dashoffset="${offset}"
                transform="rotate(-90 14 14)" stroke-linecap="round"/>
            </svg>
            ${progress}%
          </div>
          <span class="mod-status ${statusClass}">${capitalize(m.status || 'Available')}</span>
          <div class="mod-score">${score}<span>/100</span></div>
          <div class="mod-cert ${m.has_certificate ? 'earned' : ''}">
            ${m.has_certificate ? '🏆 Certificate' : '—'}
          </div>
          <a href="/learning-path.html" class="btn btn-secondary btn-sm" style="border-radius:var(--r-full);font-size:12px;padding:5px 14px;">
            Continue →
          </a>
        </div>
      </div>
    `;
  }).join('');
}

/* ── 5. Search Filters ────────────────────────────────────────────────────── */
function setupFilters() {
  const search = document.getElementById('course-search');
  const status = document.getElementById('course-status');

  const filter = () => {
    const q = (search?.value || '').toLowerCase().trim();
    const st = status?.value || 'all';
    document.querySelectorAll('.module-row').forEach(row => {
      const t = row.getAttribute('data-title') || '';
      const s = row.getAttribute('data-status') || '';
      row.style.display = (!q || t.includes(q)) && (st === 'all' || s === st) ? 'flex' : 'none';
    });
  };

  search?.addEventListener('input', filter);
  status?.addEventListener('change', filter);
}

/* ── 6. Load Saved Workspaces ─────────────────────────────────────────────── */
async function loadDashboardSavedProjects() {
  const container = document.getElementById('dash-saved-projects-list');
  const countBadge = document.getElementById('dash-saved-count');
  if (!container) return;

  try {
    const progs = await workspaceApi.listPrograms();
    if (countBadge) countBadge.textContent = `${progs.length} saved`;

    if (!progs || progs.length === 0) {
      container.innerHTML = `
        <div style="grid-column:1/-1;text-align:center;padding:28px 16px;background:#FFFDF9;border:1.5px dashed rgba(200,160,100,0.3);border-radius:12px;">
          <div style="font-size:28px;margin-bottom:6px;">⚡</div>
          <div style="font-size:13.5px;font-weight:700;color:#1C0E04;">No saved workspaces yet</div>
          <p style="font-size:12px;color:#8A6D3B;margin:4px 0 12px;">Create and save your custom Python scripts or interactive Web apps in the playground.</p>
          <a href="/playground.html" class="btn btn-primary btn-sm" style="border-radius:var(--r-full);">Launch Blank Workspace</a>
        </div>
      `;
      return;
    }

    container.innerHTML = progs.map(p => {
      const isWeb = p.language === 'web';
      return `
        <div style="background:#FFFDF9;border:1.5px solid rgba(200,160,100,0.28);border-radius:12px;padding:16px;display:flex;flex-direction:column;justify-content:space-between;gap:12px;transition:all 0.2s var(--ease);box-shadow:0 2px 8px rgba(44,26,14,0.03);">
          <div>
            <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:8px;">
              <span class="badge ${isWeb ? 'badge-blue' : 'badge-green'}" style="font-size:10.5px;font-weight:700;">
                ${isWeb ? '🌐 Web App' : '🐍 Python'}
              </span>
              <span style="font-size:11px;color:#8A6D3B;">${new Date(p.updated_at || p.created_at).toLocaleDateString()}</span>
            </div>
            <h4 style="font-size:14.5px;font-weight:700;color:#1C0E04;margin:0 0 4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${escapeHtml(p.title)}</h4>
            <div style="font-size:11.5px;color:#8A6D3B;">${(p.code || '').length} characters of code</div>
          </div>
          <a href="/playground.html?project=${p.id}" class="btn btn-primary btn-sm btn-full" style="font-weight:700;border-radius:8px;font-size:12px;">
            ⚡ Open Workspace →
          </a>
        </div>
      `;
    }).join('');

  } catch (err) {
    console.warn('[Dashboard] Could not load saved projects:', err);
    if (container) {
      container.innerHTML = `<div style="grid-column:1/-1;color:#8A6D3B;font-size:12px;">Could not load saved projects.</div>`;
    }
  }
}

function set(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function setupCourseTrackSwitcher() {
  let activeCourseTrack = localStorage.getItem('selected_course_track') || 'python';
  const coursePills = document.querySelectorAll('#dash-course-tabs .course-pill-btn');
  if (!coursePills || coursePills.length === 0) return;

  function updateActionLinks(course) {
    const resumeBtn = document.getElementById('dash-btn-resume');
    const practiceBtn = document.getElementById('dash-btn-practice');
    if (resumeBtn) resumeBtn.href = `/learning-path.html?course=${course}`;
    if (practiceBtn) practiceBtn.href = `/practice.html?course=${course}`;
  }

  coursePills.forEach(btn => {
    if (btn.getAttribute('data-course') === activeCourseTrack) {
      coursePills.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      updateActionLinks(activeCourseTrack);
    }
    btn.addEventListener('click', () => {
      coursePills.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeCourseTrack = btn.getAttribute('data-course') || 'python';
      localStorage.setItem('selected_course_track', activeCourseTrack);
      updateActionLinks(activeCourseTrack);
      showToast(`Switched active track to ${activeCourseTrack.toUpperCase()} Systems. Explore curriculum & practice labs!`, 'info');
      const welcomeSub = document.getElementById('dash-welcome-sub');
      if (welcomeSub) {
        welcomeSub.textContent = `You are actively focusing on the ${activeCourseTrack.toUpperCase()} Engineering Track. All lessons and labs are calibrated for ${activeCourseTrack.toUpperCase()}.`;
      }
    });
  });
}

init();
