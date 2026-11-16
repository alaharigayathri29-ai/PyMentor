import { adminApi, setToken, setUser } from './api.js?v=20261108_v17';
import { showToast, formatDate, navigate } from './app.js?v=20261108_v17';

let _cachedUsers = [];
let _cachedStats = null;
let _currentFilter = { q: '', skill_level: '', is_active: '' };
let _activeStudentId = null;

export async function initAdmin() {
  const el = document.getElementById('page-admin');
  el.innerHTML = `<div class="page-content"><div class="flex-center" style="height:300px"><div class="loading-spin" style="font-size:32px">⟳</div></div></div>`;
  try {
    const [users, stats] = await Promise.all([adminApi.users(), adminApi.stats()]);
    _cachedUsers = users;
    _cachedStats = stats;
    renderAdmin(users, stats);
  } catch (err) {
    el.innerHTML = `<div class="page-content"><div class="alert alert-error">${err.message}</div></div>`;
  }
}

function renderAdmin(users, stats) {
  const dist = stats.skill_level_distribution || {};

  document.getElementById('page-admin').innerHTML = `
    <div class="page-content animate-in admin-command-center">
      <div class="section-header" style="flex-wrap:wrap;gap:16px;">
        <div>
          <div style="display:flex;align-items:center;gap:10px;">
            <span class="badge badge-purple" style="font-size:11px;padding:3px 8px;letter-spacing:1px;text-transform:uppercase;">Surveillance Mode</span>
            <span style="font-size:12px;color:var(--green);">● Live Connected</span>
          </div>
          <h1 class="page-title" style="margin-top:4px;">Admin Command Center</h1>
          <p class="page-sub">Real-time student monitoring, code submission inspection, and platform analytics</p>
        </div>
        <div style="display:flex;gap:10px;align-items:center;">
          <button class="btn btn-secondary btn-sm" onclick="seedDemoAccounts()" id="btn-seed-demo">
            🌱 Seed 4 Demo Students
          </button>
          <button class="btn btn-primary btn-sm" onclick="refreshAdmin()">
            ↺ Refresh Data
          </button>
        </div>
      </div>

      <!-- Platform Analytics KPI Grid -->
      <div class="stats-grid" style="grid-template-columns:repeat(auto-fit,minmax(180px,1fr));">
        <div class="stat-card">
          <div class="stat-icon stat-icon-blue">👥</div>
          <div class="stat-value">${stats.total_students}</div>
          <div class="stat-label">Total Students (${stats.active_students || stats.total_students} Active)</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon stat-icon-green">⚡</div>
          <div class="stat-value">${stats.submission_pass_rate ?? 75}%</div>
          <div class="stat-label">Code Pass Rate</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon stat-icon-purple">🎯</div>
          <div class="stat-value">${stats.average_assessment_score}%</div>
          <div class="stat-label">Avg Quiz Score</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon stat-icon-cyan">💻</div>
          <div class="stat-value">${stats.total_submissions}</div>
          <div class="stat-label">Practice Submissions</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon stat-icon-amber">🤖</div>
          <div class="stat-value">${stats.total_mentor_sessions}</div>
          <div class="stat-label">AI Mentor Inquiries</div>
        </div>
      </div>

      <!-- Skill Level Breakdown -->
      <div style="display:grid;grid-template-columns:1fr 2fr;gap:20px;margin-bottom:24px;">
        <div class="chart-card">
          <div class="chart-title">Level Distribution</div>
          ${['beginner','intermediate','advanced'].map(level => {
            const count = dist[level] || 0;
            const total = Object.values(dist).reduce((a,b)=>a+b,0) || 1;
            const pct = Math.round(count/total*100);
            const colors = { beginner:'var(--green)', intermediate:'var(--amber)', advanced:'var(--purple)' };
            return `
              <div style="margin-bottom:14px">
                <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px">
                  <span style="text-transform:capitalize;font-weight:600;display:flex;align-items:center;gap:6px;">
                    <span style="width:8px;height:8px;border-radius:50%;background:${colors[level]};"></span>
                    ${level}
                  </span>
                  <span style="font-weight:700;color:${colors[level]}">${count} (${pct}%)</span>
                </div>
                <div class="progress-bar-wrap" style="height:8px;background:rgba(255,255,255,0.06);border-radius:4px;">
                  <div style="height:8px;border-radius:4px;background:${colors[level]};width:${pct}%;transition:width 0.6s ease"></div>
                </div>
              </div>`;
          }).join('')}
        </div>

        <div class="chart-card">
          <div class="chart-title">Student Activity & Telemetry</div>
          <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px">
            <div style="padding:16px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:12px;text-align:center">
              <div style="font-size:26px;font-weight:800;color:var(--text-accent)">${users.filter(u=>u.has_assessment).length}</div>
              <div style="font-size:12px;color:var(--text-secondary);margin-top:4px">Assessed Students</div>
            </div>
            <div style="padding:16px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:12px;text-align:center">
              <div style="font-size:26px;font-weight:800;color:var(--green)">${users.filter(u=>u.is_active).length}</div>
              <div style="font-size:12px;color:var(--text-secondary);margin-top:4px">Active Accounts</div>
            </div>
            <div style="padding:16px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:12px;text-align:center">
              <div style="font-size:26px;font-weight:800;color:var(--cyan)">${users.filter(u=>u.submission_count>0).length}</div>
              <div style="font-size:12px;color:var(--text-secondary);margin-top:4px">Coders Active</div>
            </div>
            <div style="padding:16px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:12px;text-align:center">
              <div style="font-size:26px;font-weight:800;color:var(--amber)">${users.filter(u=>u.session_count>0).length}</div>
              <div style="font-size:12px;color:var(--text-secondary);margin-top:4px">Mentor Learners</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Filter & Search Toolbar -->
      <div class="card" style="padding:14px 18px;margin-bottom:20px;display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between;background:rgba(255,255,255,0.02);">
        <div style="display:flex;flex:1;min-width:240px;gap:10px;">
          <input 
            type="text" 
            id="admin-search-input" 
            placeholder="🔍 Search student by username or email..." 
            class="input-field"
            style="width:100%;max-width:380px;font-size:13px;padding:8px 12px;border-radius:8px;background:rgba(0,0,0,0.3);"
            oninput="handleAdminSearch(this.value)"
          />
        </div>
        <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
          <select id="admin-level-filter" class="input-field" style="font-size:13px;padding:8px 12px;border-radius:8px;background:rgba(0,0,0,0.3);" onchange="handleAdminLevelFilter(this.value)">
            <option value="">All Skill Levels</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>

          <select id="admin-status-filter" class="input-field" style="font-size:13px;padding:8px 12px;border-radius:8px;background:rgba(0,0,0,0.3);" onchange="handleAdminStatusFilter(this.value)">
            <option value="">All Statuses</option>
            <option value="true">Active Only</option>
            <option value="false">Disabled Only</option>
          </select>
        </div>
      </div>

      <!-- Students Table -->
      <div class="chart-card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
          <div class="chart-title">Enrolled Students (<span id="admin-user-count">${users.length}</span>)</div>
          <span style="font-size:12px;color:var(--text-muted);">Click <strong>Inspect</strong> to view code, test outputs & AI transcripts</span>
        </div>
        <div class="table-wrap">
          <table class="data-table" id="admin-students-table">
            <thead>
              <tr>
                <th>Student</th>
                <th>Skill Level</th>
                <th>Quiz Score</th>
                <th>Practice Submissions</th>
                <th>AI Sessions</th>
                <th>Last Active</th>
                <th>Status</th>
                <th style="text-align:right">Actions</th>
              </tr>
            </thead>
            <tbody id="admin-students-tbody">
              ${renderStudentRows(users)}
            </tbody>
          </table>
        </div>
      </div>

      <!-- Student Detail Modal (Inspector) -->
      <div id="student-inspector-modal" class="modal-overlay hidden">
        <div class="modal-card" style="max-width:900px;width:95%;max-height:90vh;display:flex;flex-direction:column;padding:0;overflow:hidden;border-radius:16px;background:var(--bg-app);border:1px solid rgba(255,255,255,0.12);box-shadow:0 24px 60px rgba(0,0,0,0.7);">
          <div style="padding:20px 24px;border-bottom:1px solid rgba(255,255,255,0.08);display:flex;justify-content:space-between;align-items:center;background:rgba(255,255,255,0.02);">
            <div style="display:flex;align-items:center;gap:12px;">
              <div class="user-avatar" id="modal-student-avatar" style="width:42px;height:42px;font-size:16px;">S</div>
              <div>
                <h3 id="modal-student-username" style="font-size:18px;font-weight:700;">Student Name</h3>
                <div id="modal-student-email" style="font-size:12px;color:var(--text-muted);">email@example.com</div>
              </div>
            </div>
            <button class="btn btn-ghost btn-sm" onclick="closeStudentInspector()" style="font-size:18px;padding:4px 8px;">✕</button>
          </div>

          <!-- Modal Tabs -->
          <div style="display:flex;gap:4px;padding:0 24px;border-bottom:1px solid rgba(255,255,255,0.08);background:rgba(0,0,0,0.2);">
            <button class="tab-btn active" id="tab-btn-mastery" onclick="switchInspectorTab('mastery')">📊 Mastery & Journey</button>
            <button class="tab-btn" id="tab-btn-subs" onclick="switchInspectorTab('subs')">💻 Code Submissions</button>
            <button class="tab-btn" id="tab-btn-chats" onclick="switchInspectorTab('chats')">🤖 AI Mentor Logs</button>
          </div>

          <!-- Modal Body Content -->
          <div id="modal-tab-content" style="padding:24px;overflow-y:auto;flex:1;min-height:350px;">
            <div class="flex-center" style="height:250px;"><div class="loading-spin" style="font-size:28px">⟳</div></div>
          </div>

          <!-- Modal Footer Actions -->
          <div style="padding:14px 24px;border-top:1px solid rgba(255,255,255,0.08);display:flex;justify-content:space-between;align-items:center;background:rgba(255,255,255,0.02);">
            <div id="modal-footer-stats" style="font-size:12px;color:var(--text-muted);">Student ID: --</div>
            <div style="display:flex;gap:10px;">
              <button class="btn btn-primary btn-sm" id="modal-impersonate-btn" onclick="impersonateActiveStudent()">
                👤 Login as Student
              </button>
              <button class="btn btn-secondary btn-sm" onclick="closeStudentInspector()">
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>`;

  setupAdminGlobalHandlers();
}

function renderStudentRows(users) {
  if (!users.length) {
    return `<tr><td colspan="8" style="text-align:center;padding:32px;color:var(--text-muted);">No students match your filter criteria.</td></tr>`;
  }
  return users.map(u => {
    const levelColors = { beginner: 'badge-green', intermediate: 'badge-amber', advanced: 'badge-purple' };
    const levelBadge = u.skill_level 
      ? `<span class="badge ${levelColors[u.skill_level] || 'badge-gray'}">${u.skill_level}</span>` 
      : `<span class="badge badge-gray">Not Assessed</span>`;
    
    const quizScoreBadge = u.has_assessment 
      ? `<span style="font-weight:700;color:var(--green)">${u.assessment_score ?? 100}%</span>`
      : `<span style="color:var(--text-muted)">—</span>`;

    return `
      <tr>
        <td>
          <div style="display:flex;align-items:center;gap:10px;">
            <div class="user-avatar" style="width:32px;height:32px;font-size:12px;">${(u.username||'S').charAt(0).toUpperCase()}</div>
            <div>
              <div style="font-weight:600;font-size:13px;">${u.username}</div>
              <div style="font-size:11px;color:var(--text-muted);">${u.email}</div>
            </div>
          </div>
        </td>
        <td>${levelBadge}</td>
        <td>${quizScoreBadge}</td>
        <td>
          <span style="font-weight:600;">${u.submission_count}</span>
          ${u.submission_count > 0 ? `<span style="font-size:11px;color:var(--text-muted);margin-left:4px;">(avg ${u.avg_submission_score}%)</span>` : ''}
        </td>
        <td style="color:var(--text-muted);">${u.session_count} chats</td>
        <td style="color:var(--text-muted);font-size:12px;">${formatDate(u.last_active || u.created_at)}</td>
        <td>
          <span class="badge ${u.is_active ? 'badge-green' : 'badge-red'}">
            ${u.is_active ? 'Active' : 'Disabled'}
          </span>
        </td>
        <td style="text-align:right;">
          <div style="display:inline-flex;gap:6px;">
            <button onclick="inspectStudent(${u.id})" class="btn btn-secondary btn-sm" style="padding:4px 10px;font-size:12px;" title="Inspect Code & Progress">
              🔍 Inspect
            </button>
            <button onclick="impersonateUser(${u.id})" class="btn btn-primary btn-sm" style="padding:4px 10px;font-size:12px;" title="Impersonate & Test As Student">
              👤 Login
            </button>
            <button onclick="toggleUser(${u.id})" class="btn btn-sm ${u.is_active ? 'btn-danger' : 'btn-success'}" style="padding:4px 8px;font-size:12px;">
              ${u.is_active ? 'Disable' : 'Enable'}
            </button>
          </div>
        </td>
      </tr>`;
  }).join('');
}

function setupAdminGlobalHandlers() {
  window.refreshAdmin = initAdmin;

  window.handleAdminSearch = (val) => {
    _currentFilter.q = val.toLowerCase().trim();
    applyAdminFilters();
  };

  window.handleAdminLevelFilter = (val) => {
    _currentFilter.skill_level = val;
    applyAdminFilters();
  };

  window.handleAdminStatusFilter = (val) => {
    _currentFilter.is_active = val;
    applyAdminFilters();
  };

  window.toggleUser = async (id) => {
    try {
      const result = await adminApi.toggle(id);
      showToast(`User ${result.is_active ? 'enabled' : 'disabled'} successfully`, 'success');
      initAdmin();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  window.seedDemoAccounts = async () => {
    const btn = document.getElementById('btn-seed-demo');
    if (btn) btn.innerHTML = '⏳ Seeding...';
    try {
      const res = await adminApi.seedDemo();
      showToast(res.message || 'Demo student accounts populated!', 'success');
      await initAdmin();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      if (btn) btn.innerHTML = '🌱 Seed 4 Demo Students';
    }
  };

  window.impersonateUser = async (id) => {
    try {
      const res = await adminApi.impersonate(id);
      if (res.access_token) {
        setToken(res.access_token);
        setUser(res.user);
        showToast(`Logged in as student ${res.user.username}`, 'success');
        navigate('dashboard');
        window.location.reload();
      }
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  window.impersonateActiveStudent = () => {
    if (_activeStudentId) {
      window.impersonateUser(_activeStudentId);
    }
  };

  window.inspectStudent = async (id) => {
    _activeStudentId = id;
    const modal = document.getElementById('student-inspector-modal');
    modal.classList.remove('hidden');

    const u = _cachedUsers.find(x => x.id === id);
    if (u) {
      document.getElementById('modal-student-username').textContent = u.username;
      document.getElementById('modal-student-email').textContent = u.email;
      document.getElementById('modal-student-avatar').textContent = (u.username||'S').charAt(0).toUpperCase();
      document.getElementById('modal-footer-stats').textContent = `Student ID: #${u.id} | Level: ${u.skill_level || 'Pending'}`;
    }

    switchInspectorTab('mastery');
  };

  window.closeStudentInspector = () => {
    const modal = document.getElementById('student-inspector-modal');
    if (modal) modal.classList.add('hidden');
    _activeStudentId = null;
  };

  window.switchInspectorTab = async (tabName) => {
    ['mastery', 'subs', 'chats'].forEach(t => {
      const btn = document.getElementById(`tab-btn-${t}`);
      if (btn) btn.classList.toggle('active', t === tabName);
    });

    const content = document.getElementById('modal-tab-content');
    content.innerHTML = `<div class="flex-center" style="height:250px;"><div class="loading-spin" style="font-size:28px">⟳</div></div>`;

    try {
      if (tabName === 'mastery') {
        const detail = await adminApi.detail(_activeStudentId);
        renderInspectorMastery(detail, content);
      } else if (tabName === 'subs') {
        const subs = await adminApi.submissions(_activeStudentId);
        renderInspectorSubmissions(subs, content);
      } else if (tabName === 'chats') {
        const sessions = await adminApi.sessions(_activeStudentId);
        renderInspectorChats(sessions, content);
      }
    } catch (err) {
      content.innerHTML = `<div class="alert alert-error">${err.message}</div>`;
    }
  };
}

function applyAdminFilters() {
  let filtered = _cachedUsers.slice();

  if (_currentFilter.q) {
    filtered = filtered.filter(u => 
      u.username.toLowerCase().includes(_currentFilter.q) || 
      u.email.toLowerCase().includes(_currentFilter.q)
    );
  }
  if (_currentFilter.skill_level) {
    filtered = filtered.filter(u => u.skill_level === _currentFilter.skill_level);
  }
  if (_currentFilter.is_active !== '') {
    const activeBool = _currentFilter.is_active === 'true';
    filtered = filtered.filter(u => u.is_active === activeBool);
  }

  const countEl = document.getElementById('admin-user-count');
  if (countEl) countEl.textContent = filtered.length;

  const tbody = document.getElementById('admin-students-tbody');
  if (tbody) tbody.innerHTML = renderStudentRows(filtered);
}

function renderInspectorMastery(detail, container) {
  const lp = detail.learning_path || {};
  const metrics = detail.metrics || {};
  const attempts = detail.assessment_attempts || [];
  const mastery = detail.mastery_breakdown || [];

  container.innerHTML = `
    <div>
      <!-- High Level Summary Cards -->
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-bottom:20px;">
        <div style="padding:12px;background:rgba(255,255,255,0.03);border-radius:10px;text-align:center;">
          <div style="font-size:18px;font-weight:700;color:var(--text-accent);text-transform:capitalize;">${lp.skill_level}</div>
          <div style="font-size:11px;color:var(--text-secondary);">Current Path</div>
        </div>
        <div style="padding:12px;background:rgba(255,255,255,0.03);border-radius:10px;text-align:center;">
          <div style="font-size:18px;font-weight:700;color:var(--green);">${metrics.passed_submissions}/${metrics.submissions_count}</div>
          <div style="font-size:11px;color:var(--text-secondary);">Problems Passed</div>
        </div>
        <div style="padding:12px;background:rgba(255,255,255,0.03);border-radius:10px;text-align:center;">
          <div style="font-size:18px;font-weight:700;color:var(--cyan);">${attempts.length ? attempts[0].score + '%' : '—'}</div>
          <div style="font-size:11px;color:var(--text-secondary);">Assessment Score</div>
        </div>
        <div style="padding:12px;background:rgba(255,255,255,0.03);border-radius:10px;text-align:center;">
          <div style="font-size:18px;font-weight:700;color:var(--amber);">${metrics.sessions_count}</div>
          <div style="font-size:11px;color:var(--text-secondary);">AI Chat Sessions</div>
        </div>
      </div>

      <!-- Topic Mastery Breakdown Grid -->
      <h4 style="font-size:14px;margin-bottom:12px;font-weight:600;">Python Topics Mastery (BYJU'S Radar Data)</h4>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin-bottom:24px;">
        ${mastery.map(m => {
          const score = Math.round(m.mastery_score || 0);
          const color = score >= 70 ? 'var(--green)' : (score >= 40 ? 'var(--amber)' : 'var(--text-muted)');
          return `
            <div style="padding:12px 14px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:10px;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                <span style="font-size:13px;font-weight:600;">${m.icon || '📚'} ${m.topic_name}</span>
                <span style="font-size:12px;font-weight:700;color:${color}">${score}%</span>
              </div>
              <div class="progress-bar-wrap" style="height:6px;background:rgba(255,255,255,0.06);border-radius:3px;">
                <div style="height:6px;border-radius:3px;background:${color};width:${score}%;"></div>
              </div>
              <div style="display:flex;justify-content:space-between;font-size:11px;color:var(--text-muted);margin-top:6px;">
                <span>Status: <strong style="color:var(--text-primary);text-transform:capitalize;">${m.status}</strong></span>
                <span>${m.attempts} attempts</span>
              </div>
            </div>`;
        }).join('')}
      </div>

      <!-- Assessment History -->
      <h4 style="font-size:14px;margin-bottom:12px;font-weight:600;">Assessment Attempts</h4>
      ${attempts.length ? `
        <table class="data-table" style="font-size:12px;">
          <thead>
            <tr>
              <th>Date</th>
              <th>Assigned Level</th>
              <th>Overall Score</th>
              <th>Topic Breakdown</th>
            </tr>
          </thead>
          <tbody>
            ${attempts.map(a => `
              <tr>
                <td>${formatDate(a.completed_at)}</td>
                <td><span class="badge badge-purple">${a.skill_level}</span></td>
                <td><strong style="color:var(--green)">${a.score}%</strong></td>
                <td>${Object.entries(a.topic_scores || {}).map(([k,v]) => `${k}: ${v}%`).join(', ') || 'Standard test'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      ` : `<div style="font-size:12px;color:var(--text-muted);padding:8px 0;">No assessment taken yet.</div>`}
    </div>`;
}

function renderInspectorSubmissions(subs, container) {
  if (!subs.length) {
    container.innerHTML = `
      <div class="empty-state" style="padding:40px 20px;">
        <div class="empty-state-icon">💻</div>
        <h3>No Code Submissions</h3>
        <p>This student has not submitted any practice problems yet.</p>
      </div>`;
    return;
  }

  container.innerHTML = `
    <div>
      <div style="margin-bottom:16px;display:flex;justify-content:space-between;align-items:center;">
        <span style="font-size:13px;color:var(--text-muted);">Total Submissions: ${subs.length}</span>
      </div>
      <div style="display:flex;flex-direction:column;gap:16px;">
        ${subs.map((s, idx) => {
          const pass = s.score >= 70;
          return `
            <div class="card" style="padding:16px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.08);">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                <div>
                  <strong style="font-size:15px;">#${subs.length - idx} ${s.problem_title}</strong>
                  <span class="badge badge-gray" style="margin-left:8px;font-size:11px;">${s.difficulty}</span>
                </div>
                <div style="display:flex;align-items:center;gap:10px;">
                  <span class="badge ${pass ? 'badge-green' : 'badge-red'}">${s.passed_cases}/${s.total_cases} Passed (${s.score}%)</span>
                  <span style="font-size:11px;color:var(--text-muted);">${formatDate(s.submitted_at)}</span>
                </div>
              </div>
              
              <!-- Code Snippet Box -->
              <div style="margin-top:8px;position:relative;">
                <pre style="background:#090d16;padding:12px 14px;border-radius:8px;border:1px solid rgba(255,255,255,0.06);color:#e2e8f0;font-family:'JetBrains Mono',monospace;font-size:12px;line-height:1.5;overflow-x:auto;"><code>${escapeHtml(s.code || '# No code')}</code></pre>
              </div>

              <!-- Feedback / Execution Output -->
              ${s.feedback ? `
                <div style="margin-top:10px;padding:8px 12px;background:rgba(255,255,255,0.02);border-left:3px solid ${pass ? 'var(--green)' : 'var(--red)'};border-radius:4px;font-size:12px;color:var(--text-secondary);">
                  <strong>Test Harness Feedback:</strong> ${escapeHtml(s.feedback)}
                </div>
              ` : ''}
            </div>`;
        }).join('')}
      </div>
    </div>`;
}

function renderInspectorChats(sessions, container) {
  if (!sessions.length) {
    container.innerHTML = `
      <div class="empty-state" style="padding:40px 20px;">
        <div class="empty-state-icon">🤖</div>
        <h3>No AI Mentor Chats</h3>
        <p>This student hasn't initiated any AI mentor conversations yet.</p>
      </div>`;
    return;
  }

  container.innerHTML = `
    <div>
      <div style="margin-bottom:14px;font-size:13px;color:var(--text-muted);">
        Found ${sessions.length} conversation session(s)
      </div>
      <div style="display:flex;flex-direction:column;gap:20px;">
        ${sessions.map(sess => `
          <div class="card" style="padding:16px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.08);">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.06);padding-bottom:8px;">
              <strong style="font-size:14px;color:var(--text-accent);">💬 ${sess.title}</strong>
              <span style="font-size:11px;color:var(--text-muted);">${formatDate(sess.created_at)}</span>
            </div>
            <div style="display:flex;flex-direction:column;gap:10px;max-height:350px;overflow-y:auto;padding-right:6px;">
              ${sess.messages.map(m => {
                const isUser = m.role === 'user';
                return `
                  <div style="display:flex;gap:10px;align-items:flex-start;${isUser ? 'flex-direction:row-reverse;' : ''}">
                    <div style="width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;flex-shrink:0;background:${isUser ? 'var(--purple)' : '#1e293b'};">
                      ${isUser ? '👤' : '🤖'}
                    </div>
                    <div style="max-width:82%;padding:10px 14px;border-radius:12px;font-size:12px;line-height:1.5;background:${isUser ? 'rgba(124,58,237,0.18)' : 'rgba(255,255,255,0.04)'};border:1px solid ${isUser ? 'rgba(124,58,237,0.3)' : 'rgba(255,255,255,0.06)'};color:var(--text-primary);">
                      <div style="font-size:10px;color:var(--text-muted);margin-bottom:4px;font-weight:600;">${isUser ? 'Student' : 'PyMentor'}</div>
                      <div style="white-space:pre-wrap;">${escapeHtml(m.content)}</div>
                    </div>
                  </div>`;
              }).join('')}
            </div>
          </div>
        `).join('')}
      </div>
    </div>`;
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}
