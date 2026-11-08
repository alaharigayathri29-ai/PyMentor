/**
 * admin/students.js
 * Admin Student Management & Inspection Controller (Real Multi-Page Application)
 * Direct inspection of student dossiers without impersonation.
 */

import { requireAuth, initLayout, escapeHtml } from '../common.js?v=20261108_v17';
import { adminApi } from '../api.js?v=20261108_v17';
import { showToast } from '../components/toast.js?v=20261108_v17';
import { capitalize, formatDate, formatRelative } from '../utils/formatters.js?v=20261108_v17';

let activeStudentId = null;

async function init() {
  const user = await requireAuth({ requireAdmin: true });
  if (!user) return;

  initLayout('admin-students', user);

  const searchInput = document.getElementById('adm-student-search');
  const levelSelect = document.getElementById('adm-student-level-filter');
  const statusSelect = document.getElementById('adm-student-status-filter');
  const refreshBtn = document.getElementById('btn-refresh-students');
  const closeDossierBtn = document.getElementById('btn-close-dossier');
  const dossierModal = document.getElementById('adm-dossier-modal');

  const fetchFilteredStudents = () => {
    const params = {
      q: searchInput?.value.trim() || '',
      skill_level: levelSelect?.value || '',
      is_active: statusSelect?.value || '',
    };
    loadStudentsTable(params);
  };

  searchInput?.addEventListener('input', debounce(fetchFilteredStudents, 300));
  levelSelect?.addEventListener('change', fetchFilteredStudents);
  statusSelect?.addEventListener('change', fetchFilteredStudents);
  refreshBtn?.addEventListener('click', fetchFilteredStudents);

  closeDossierBtn?.addEventListener('click', () => {
    dossierModal?.classList.add('hidden');
  });

  dossierModal?.addEventListener('click', (e) => {
    if (e.target === dossierModal) dossierModal.classList.add('hidden');
  });

  // Dossier sub-tabs
  const tabMastery = document.getElementById('dossier-tab-mastery');
  const tabSubs = document.getElementById('dossier-tab-subs');
  const tabAssess = document.getElementById('dossier-tab-assess');

  tabMastery?.addEventListener('click', () => switchDossierTab('mastery'));
  tabSubs?.addEventListener('click', () => switchDossierTab('subs'));
  tabAssess?.addEventListener('click', () => switchDossierTab('assess'));

  // Initial load
  loadStudentsTable();
}

async function loadStudentsTable(params = {}) {
  const tbody = document.getElementById('adm-students-tbody');
  if (!tbody) return;
  tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:24px;"><div class="spinner" style="margin:0 auto;"></div></td></tr>`;

  try {
    const students = await adminApi.users(params);
    if (!students || students.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:24px;color:var(--text-muted);">No students matched your search criteria.</td></tr>`;
      return;
    }

    tbody.innerHTML = students.map(s => {
      const levelClass = s.skill_level === 'beginner'
        ? 'badge-beginner'
        : (s.skill_level === 'intermediate' ? 'badge-intermediate' : (s.skill_level === 'advanced' ? 'badge-advanced' : 'badge-gray'));

      return `
        <tr>
          <td>
            <div style="font-weight:700;color:var(--text-primary);">${escapeHtml(s.username)}</div>
            <div style="font-size:11px;color:var(--text-secondary);">${escapeHtml(s.email)}</div>
          </td>
          <td><span class="badge ${levelClass}">${capitalize(s.skill_level || 'unassessed')}</span></td>
          <td>
            ${s.has_assessment
              ? `<span style="font-weight:700;color:${s.assessment_score >= 70 ? 'var(--success-hover)' : 'var(--highlight-hover)'};">${Math.round(s.assessment_score)}%</span>`
              : '<span style="color:var(--text-muted);font-size:12px;">Not Taken</span>'
            }
          </td>
          <td>
            <div style="font-weight:600;color:var(--text-primary);">${s.submission_count}</div>
            <div style="font-size:11px;color:var(--text-secondary);">${s.avg_submission_score}% avg</div>
          </td>
          <td>${s.session_count || 0}</td>
          <td><span style="font-size:12px;color:var(--text-muted);">${formatRelative(s.last_active)}</span></td>
          <td>
            <span class="badge ${s.is_active ? 'badge-green' : 'badge-red'}">
              ${s.is_active ? 'Active' : 'Disabled'}
            </span>
          </td>
          <td>
            <div style="display:flex;gap:6px;">
              <button class="btn btn-secondary btn-sm btn-inspect-student" data-id="${s.id}" style="padding:4px 10px;font-size:12px;">
                Inspect
              </button>
              <button class="btn btn-ghost btn-sm btn-toggle-active" data-id="${s.id}" style="padding:4px 8px;font-size:12px;">
                ${s.is_active ? 'Disable' : 'Enable'}
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join('');

    // Inspect dossier handler
    tbody.querySelectorAll('.btn-inspect-student').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = parseInt(btn.getAttribute('data-id'), 10);
        openStudentDossier(id);
      });
    });

    // Toggle active handler
    tbody.querySelectorAll('.btn-toggle-active').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = parseInt(btn.getAttribute('data-id'), 10);
        try {
          const res = await adminApi.toggle(id);
          showToast(`Student account ${res.is_active ? 'activated' : 'disabled'}`, 'info');
          loadStudentsTable(params);
        } catch (err) {
          showToast(err.message, 'error');
        }
      });
    });

  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:20px;color:var(--red);">${err.message}</td></tr>`;
  }
}

async function openStudentDossier(studentId) {
  activeStudentId = studentId;
  const modal = document.getElementById('adm-dossier-modal');
  if (!modal) return;

  modal.classList.remove('hidden');

  const nameEl = document.getElementById('dossier-name');
  const metaEl = document.getElementById('dossier-meta');
  const levelEl = document.getElementById('dossier-level');
  const subsEl = document.getElementById('dossier-subs-count');
  const sessionsEl = document.getElementById('dossier-sessions-count');

  if (nameEl) nameEl.textContent = 'Loading Student Dossier…';

  try {
    const detail = await adminApi.detail(studentId);
    window.currentDossierData = detail;

    if (nameEl) nameEl.textContent = detail.profile.username;
    if (metaEl) metaEl.textContent = `${detail.profile.email} • ID #${detail.profile.id} • Registered ${formatDate(detail.profile.created_at)}`;
    if (levelEl) levelEl.textContent = capitalize(detail.learning_path.skill_level || 'unassessed');
    if (subsEl) subsEl.textContent = `${detail.metrics.passed_submissions}/${detail.metrics.submissions_count} Passed`;
    if (sessionsEl) sessionsEl.textContent = detail.metrics.sessions_count;

    switchDossierTab('mastery');

  } catch (err) {
    showToast(`Failed to load student detail: ${err.message}`, 'error');
  }
}

function switchDossierTab(tabKey) {
  const tabs = {
    mastery: document.getElementById('dossier-tab-mastery'),
    subs: document.getElementById('dossier-tab-subs'),
    assess: document.getElementById('dossier-tab-assess'),
  };
  Object.values(tabs).forEach(t => t?.classList.remove('active'));
  tabs[tabKey]?.classList.add('active');

  const body = document.getElementById('dossier-tab-body');
  if (!body || !window.currentDossierData) return;

  const data = window.currentDossierData;

  if (tabKey === 'mastery') {
    const items = data.mastery_breakdown || [];
    body.innerHTML = `
      <div style="font-size:13px;font-weight:700;color:var(--text-primary);margin-bottom:12px;">Curriculum Topic Mastery</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
        ${items.map(m => `
          <div style="padding:12px;background:#F8FAFC;border:1px solid var(--border);border-radius:8px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
              <span style="font-weight:600;font-size:13px;color:var(--text-primary);">${m.icon || '📚'} ${escapeHtml(m.topic_name)}</span>
              <span class="badge ${m.status === 'completed' ? 'badge-green' : 'badge-purple'}">${Math.round(m.mastery_score)}%</span>
            </div>
            <div class="progress-bar-wrap" style="height:5px;">
              <div class="progress-bar-fill" style="width:${m.mastery_score}%;background:${m.status === 'completed' ? 'var(--success)' : 'var(--primary)'};"></div>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  } else if (tabKey === 'subs') {
    body.innerHTML = '<div style="padding:20px;text-align:center;"><div class="spinner"></div></div>';
    adminApi.submissions(activeStudentId).then(subs => {
      if (!subs || subs.length === 0) {
        body.innerHTML = '<div style="padding:20px;text-align:center;color:var(--text-muted);font-size:13px;">No coding submissions recorded for this student.</div>';
        return;
      }
      body.innerHTML = `
        <div style="font-size:13px;font-weight:700;color:var(--text-primary);margin-bottom:12px;">Code Submissions (${subs.length})</div>
        <div style="display:flex;flex-direction:column;gap:8px;max-height:300px;overflow-y:auto;">
          ${subs.map(s => `
            <div style="padding:10px 14px;background:#F8FAFC;border:1px solid var(--border);border-radius:8px;display:flex;justify-content:space-between;align-items:center;">
              <div>
                <div style="font-weight:600;font-size:13px;color:var(--text-primary);">${escapeHtml(s.problem_title)}</div>
                <div style="font-size:11px;color:var(--text-secondary);">${formatRelative(s.submitted_at)}</div>
              </div>
              <span class="badge ${s.score >= 70 ? 'badge-green' : 'badge-red'}">
                ${s.passed_cases}/${s.total_cases} Passed (${Math.round(s.score)}%)
              </span>
            </div>
          `).join('')}
        </div>
      `;
    });
  } else if (tabKey === 'assess') {
    const attempts = data.assessment_attempts || [];
    if (attempts.length === 0) {
      body.innerHTML = '<div style="padding:20px;text-align:center;color:var(--text-muted);font-size:13px;">No diagnostic assessment attempts on record.</div>';
      return;
    }
    body.innerHTML = `
      <div style="font-size:13px;font-weight:700;color:var(--text-primary);margin-bottom:12px;">Diagnostic Assessment History (${attempts.length})</div>
      <div style="display:flex;flex-direction:column;gap:10px;">
        ${attempts.map(a => `
          <div style="padding:14px;background:#F8FAFC;border:1px solid var(--border);border-radius:8px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
              <div>
                <span class="badge badge-purple">${capitalize(a.skill_level || 'beginner')}</span>
                <span style="font-size:14px;font-weight:700;color:var(--text-primary);margin-left:8px;">${Math.round(a.score || 0)}% Score</span>
              </div>
              <span style="font-size:11px;color:var(--text-secondary);">${formatDate(a.completed_at)}</span>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  }
}

function debounce(fn, delay) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn(...args), delay);
  };
}

init();

