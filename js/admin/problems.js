/**
 * admin/problems.js
 * Admin Coding Problems Management (Real Multi-Page Application)
 */

import { requireAuth, initLayout, escapeHtml } from '../common.js?v=20261108_v17';
import { adminApi } from '../api.js?v=20261108_v17';
import { showToast } from '../components/toast.js?v=20261108_v17';
import { capitalize } from '../utils/formatters.js?v=20261108_v17';

let cachedProblems = [];
let cachedTopics = [];

async function init() {
  const user = await requireAuth({ requireAdmin: true });
  if (!user) return;

  initLayout('admin-problems', user);

  setupModal();
  setupFilters();
  await loadProblems();
}

function setupModal() {
  const modal = document.getElementById('modal-create-problem');
  const openBtn = document.getElementById('btn-show-add-problem');
  const closeBtn = document.getElementById('btn-close-prob-modal');
  const cancelBtn = document.getElementById('btn-cancel-prob');

  openBtn?.addEventListener('click', () => modal?.classList.remove('hidden'));
  closeBtn?.addEventListener('click', () => modal?.classList.add('hidden'));
  cancelBtn?.addEventListener('click', () => modal?.classList.add('hidden'));

  modal?.addEventListener('click', (e) => {
    if (e.target === modal) modal.classList.add('hidden');
  });

  document.getElementById('form-create-problem')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const saveBtn = document.getElementById('btn-save-problem');
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<span>Saving…</span>';

    const testCall = document.getElementById('new-prob-test-call')?.value.trim() || 'solution()';
    const testExp = document.getElementById('new-prob-test-exp')?.value.trim() || 'True';
    const hintText = document.getElementById('new-prob-hints')?.value.trim() || '';

    const payload = {
      title: document.getElementById('new-prob-title')?.value.trim(),
      topic_id: parseInt(document.getElementById('new-prob-topic')?.value || '1', 10),
      difficulty: document.getElementById('new-prob-diff')?.value || 'easy',
      description: document.getElementById('new-prob-desc')?.value.trim(),
      starter_code: document.getElementById('new-prob-starter')?.value || 'def solution():\n    pass\n',
      test_cases: [
        {
          call: testCall,
          expected_output: testExp,
          description: 'Basic verification test case',
        },
      ],
      hints: hintText ? hintText.split('\n').filter(Boolean) : ['Review Python syntax and logic'],
    };

    try {
      await adminApi.createProblem(payload);
      showToast('Coding challenge created successfully!', 'success');
      modal?.classList.add('hidden');
      document.getElementById('form-create-problem')?.reset();
      await loadProblems();
    } catch (err) {
      showToast(`Failed to create challenge: ${err.message}`, 'error');
    } finally {
      saveBtn.disabled = false;
      saveBtn.innerHTML = '<span>Create Practice Challenge</span>';
    }
  });
}

function setupFilters() {
  const searchInput = document.getElementById('prob-search');
  const diffFilter = document.getElementById('prob-diff-filter');

  const applyFilters = () => {
    const q = (searchInput?.value || '').toLowerCase();
    const diff = diffFilter?.value || '';

    const filtered = cachedProblems.filter(p => {
      const matchQ = !q || p.title.toLowerCase().includes(q) || (p.topic_name || '').toLowerCase().includes(q);
      const matchDiff = !diff || p.difficulty === diff;
      return matchQ && matchDiff;
    });

    renderProblems(filtered);
  };

  searchInput?.addEventListener('input', applyFilters);
  diffFilter?.addEventListener('change', applyFilters);
}

async function loadProblems() {
  const container = document.getElementById('problems-list-container');
  const countBadge = document.getElementById('adm-problems-count');
  const topicSelect = document.getElementById('new-prob-topic');

  if (container) {
    container.innerHTML = '<div style="padding:40px;text-align:center;"><div class="spinner"></div></div>';
  }

  try {
    const data = await adminApi.getContentItems();
    cachedProblems = data.problems || [];
    cachedTopics = data.topics || [];

    if (countBadge) countBadge.textContent = cachedProblems.length;

    if (topicSelect) {
      topicSelect.innerHTML = cachedTopics.map(t => `<option value="${t.id}">${escapeHtml(t.name)}</option>`).join('');
    }

    renderProblems(cachedProblems);
  } catch (err) {
    showToast(`Failed to load problems: ${err.message}`, 'error');
    if (container) {
      container.innerHTML = `<div style="padding:30px;color:var(--red);text-align:center;">Failed to load problems: ${escapeHtml(err.message)}</div>`;
    }
  }
}

function renderProblems(problems) {
  const container = document.getElementById('problems-list-container');
  if (!container) return;

  if (problems.length === 0) {
    container.innerHTML = `
      <div style="text-align:center;padding:50px 20px;">
        <div style="font-size:36px;margin-bottom:10px;">🧩</div>
        <div style="font-weight:600;font-size:15px;color:var(--text-primary);margin-bottom:6px;">No Coding Challenges Found</div>
        <p style="font-size:13px;color:var(--text-secondary);margin:0 auto 16px;max-width:320px;">No practice problems matched your current filters. Add a new problem or clear your search.</p>
      </div>
    `;
    return;
  }

  const badgeClass = {
    easy: 'badge-beginner',
    medium: 'badge-intermediate',
    hard: 'badge-advanced',
  };

  container.innerHTML = `
    <table class="admin-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Challenge Title</th>
          <th>Curriculum Topic</th>
          <th>Difficulty</th>
          <th>Test Cases</th>
          <th style="text-align:right;">Actions</th>
        </tr>
      </thead>
      <tbody>
        ${problems.map(p => `
          <tr>
            <td style="font-family:var(--font-mono);font-size:12px;color:var(--text-muted);">#${p.id}</td>
            <td>
              <div style="font-weight:600;color:var(--text-primary);font-size:13px;">${escapeHtml(p.title)}</div>
            </td>
            <td>
              <span style="font-size:12px;color:var(--text-secondary);">${escapeHtml(p.topic_name || 'General')}</span>
            </td>
            <td>
              <span class="badge ${badgeClass[p.difficulty] || 'badge-intermediate'}">
                ${capitalize(p.difficulty || 'medium')}
              </span>
            </td>
            <td>
              <span class="badge badge-purple" style="font-size:11px;">${p.test_count || 1} Tests</span>
            </td>
            <td style="text-align:right;">
              <button class="btn btn-ghost btn-sm btn-del-prob" data-id="${p.id}" data-title="${escapeHtml(p.title)}" style="color:var(--red);padding:4px 8px;" title="Delete Challenge">
                <span>✕ Delete</span>
              </button>
            </td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;

  container.querySelectorAll('.btn-del-prob').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = parseInt(btn.getAttribute('data-id'), 10);
      const title = btn.getAttribute('data-title');
      if (confirm(`Are you sure you want to delete coding challenge "${title}" (#${id})?`)) {
        try {
          await adminApi.deleteProblem(id);
          showToast(`Challenge "${title}" deleted`, 'info');
          await loadProblems();
        } catch (err) {
          showToast(`Delete failed: ${err.message}`, 'error');
        }
      }
    });
  });
}

init();

