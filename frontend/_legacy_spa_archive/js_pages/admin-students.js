/**
 * Admin Student Management & Progress Inspection Controller.
 * Direct inspection without credentials switching or impersonation.
 */

import { adminApi } from '../api.js';
import { showToast } from '../components/toast.js';
import { capitalize, formatDate, formatRelative } from '../utils/formatters.js';

let activeStudentId = null;

export async function initAdminStudents() {
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
  tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:24px;"><div class="loading-spin">⟳</div></td></tr>`;

  try {
    const students = await adminApi.users(params);
    if (!students || students.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:24px;color:var(--text-muted);">No students matched your search criteria.</td></tr>`;
      return;
    }

    tbody.innerHTML = students.map(s => `
      <tr>
        <td style="font-weight:700;color:#fff;">${escapeHtml(s.username)}</td>
        <td>${escapeHtml(s.email)}</td>
        <td><span class="badge badge-purple">${capitalize(s.skill_level || 'unassessed')}</span></td>
        <td>${s.assessment_score !== null ? `${Math.round(s.assessment_score)}%` : '—'}</td>
        <td>${s.submission_count || 0}</td>
        <td>${s.avg_submission_score ? `${s.avg_submission_score}%` : '—'}</td>
        <td>
          <span class="badge ${s.is_active ? 'badge-green' : 'badge-red'}">${s.is_active ? 'Active' : 'Disabled'}</span>
        </td>
        <td>
          <div style="display:flex;gap:6px;">
            <button class="btn btn-primary btn-sm" onclick="window.inspectStudentDossier(${s.id})">
              <span>Inspect</span>
            </button>
            <button class="btn ${s.is_active ? 'btn-danger' : 'btn-secondary'} btn-sm" onclick="window.toggleStudentActive(${s.id})">
              <span>${s.is_active ? 'Disable' : 'Enable'}</span>
            </button>
          </div>
        </td>
      </tr>
    `).join('');

    window.toggleStudentActive = async (id) => {
      try {
        await adminApi.toggle(id);
        showToast('Student status toggled.', 'info');
        loadStudentsTable(params);
      } catch (err) {
        showToast(err.message, 'error');
      }
    };

    window.inspectStudentDossier = (id) => {
      activeStudentId = id;
      openDossierModal(id);
    };

  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;color:var(--red);padding:20px;">${err.message}</td></tr>`;
  }
}

async function openDossierModal(studentId) {
  const modal = document.getElementById('adm-dossier-modal');
  const titleEl = document.getElementById('dossier-student-title');
  const emailEl = document.getElementById('dossier-student-email');
  modal?.classList.remove('hidden');

  if (titleEl) titleEl.textContent = 'Loading Student Dossier…';
  if (emailEl) emailEl.textContent = '';

  try {
    const detail = await adminApi.detail(studentId);
    if (titleEl) titleEl.textContent = `${detail.profile.username}'s Learning Dossier`;
    if (emailEl) emailEl.textContent = `${detail.profile.email} • Level: ${capitalize(detail.learning_path.skill_level)}`;

    window.activeStudentDetail = detail;
    switchDossierTab('mastery');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function switchDossierTab(tabName) {
  const tabs = ['mastery', 'subs', 'assess'];
  tabs.forEach(t => {
    const btn = document.getElementById(`dossier-tab-${t}`);
    btn?.classList.toggle('active', t === tabName);
  });

  const body = document.getElementById('dossier-content-body');
  if (!body || !window.activeStudentDetail) return;
  const detail = window.activeStudentDetail;

  if (tabName === 'mastery') {
    const mastery = detail.mastery_breakdown || [];
    body.innerHTML = `
      <div style="font-size:13px;font-weight:700;color:#fff;margin-bottom:12px;">Topic Mastery Overview</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
        ${mastery.map(m => `
          <div style="padding:12px 14px;background:rgba(255,255,255,0.02);border:1px solid var(--border);border-radius:8px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
              <span style="font-weight:600;font-size:13px;color:#fff;">${m.icon || '📚'} ${m.topic_name}</span>
              <span class="badge ${m.mastery_score >= 70 ? 'badge-green' : 'badge-purple'}">${Math.round(m.mastery_score)}%</span>
            </div>
            <div class="progress-bar-wrap" style="height:5px;">
              <div class="progress-bar-fill" style="width:${Math.min(100, m.mastery_score)}%;"></div>
            </div>
            <div style="font-size:11px;color:var(--text-muted);margin-top:4px;">Status: ${capitalize(m.status)} • ${m.attempts} attempts</div>
          </div>
        `).join('')}
      </div>
    `;
  } else if (tabName === 'subs') {
    body.innerHTML = `<div class="flex-center" style="padding:20px;"><div class="loading-spin">⟳</div></div>`;
    try {
      const subs = await adminApi.submissions(activeStudentId);
      if (!subs || subs.length === 0) {
        body.innerHTML = '<div style="font-size:13px;color:var(--text-muted);text-align:center;padding:24px;">No practice submissions from this student.</div>';
        return;
      }
      body.innerHTML = `
        <div style="font-size:13px;font-weight:700;color:#fff;margin-bottom:12px;">All Submissions (${subs.length})</div>
        <div style="display:flex;flex-direction:column;gap:10px;">
          ${subs.map(s => `
            <div style="padding:12px 16px;background:rgba(255,255,255,0.02);border:1px solid var(--border);border-radius:8px;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                <span style="font-weight:700;color:#fff;font-size:13px;">${escapeHtml(s.problem_title)}</span>
                <span class="badge ${s.score >= 70 ? 'badge-green' : 'badge-red'}">${s.passed_cases}/${s.total_cases} Passed (${Math.round(s.score)}%)</span>
              </div>
              <pre style="margin:8px 0;padding:10px;background:#090d18;border-radius:6px;font-size:12px;color:#cbd5e1;max-height:120px;overflow-y:auto;"><code>${escapeHtml(s.code || '')}</code></pre>
              <div style="font-size:11px;color:var(--text-muted);">${formatRelative(s.submitted_at)}</div>
            </div>
          `).join('')}
        </div>
      `;
    } catch (err) {
      body.innerHTML = `<div class="alert alert-error">${err.message}</div>`;
    }
  } else if (tabName === 'assess') {
    const attempts = detail.assessment_attempts || [];
    if (attempts.length === 0) {
      body.innerHTML = '<div style="font-size:13px;color:var(--text-muted);text-align:center;padding:24px;">No assessment attempts on record.</div>';
      return;
    }
    body.innerHTML = `
      <div style="font-size:13px;font-weight:700;color:#fff;margin-bottom:12px;">Diagnostic Assessment Attempts (${attempts.length})</div>
      <div style="display:flex;flex-direction:column;gap:10px;">
        ${attempts.map(a => `
          <div style="padding:14px;background:rgba(255,255,255,0.02);border:1px solid var(--border);border-radius:8px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
              <div>
                <span class="badge badge-purple">${capitalize(a.skill_level || 'beginner')}</span>
                <span style="font-size:14px;font-weight:700;color:#fff;margin-left:8px;">${Math.round(a.score || 0)}% Score</span>
              </div>
              <span style="font-size:11px;color:var(--text-muted);">${formatDate(a.completed_at)}</span>
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

function escapeHtml(str) {
  return (str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

