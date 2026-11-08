/**
 * admin-topics.js
 * Admin Curriculum & Content Manager
 */
import { adminApi } from '../api.js';
import { toast } from '../components/toast.js';

let cachedTopics = [];

export async function initAdminTopics() {
  setupModalHandlers();
  await loadContent();
}

function setupModalHandlers() {
  const probModal = document.getElementById('modal-create-problem');
  const qModal = document.getElementById('modal-create-question');

  document.getElementById('btn-show-add-problem')?.addEventListener('click', () => {
    probModal?.classList.remove('hidden');
  });

  document.getElementById('btn-close-prob-modal')?.addEventListener('click', () => {
    probModal?.classList.add('hidden');
  });

  document.getElementById('btn-show-add-question')?.addEventListener('click', () => {
    qModal?.classList.remove('hidden');
  });

  document.getElementById('btn-close-q-modal')?.addEventListener('click', () => {
    qModal?.classList.add('hidden');
  });

  // Close modals on background click
  probModal?.addEventListener('click', (e) => {
    if (e.target === probModal) probModal.classList.add('hidden');
  });
  qModal?.addEventListener('click', (e) => {
    if (e.target === qModal) qModal.classList.add('hidden');
  });

  // Handle problem form submit
  document.getElementById('form-create-problem')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const saveBtn = document.getElementById('btn-save-problem');
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<span class="spinner" style="width:14px;height:14px;"></span> Saving...';

    const payload = {
      title: document.getElementById('new-prob-title')?.value.trim(),
      topic_id: parseInt(document.getElementById('new-prob-topic')?.value || '1', 10),
      difficulty: document.getElementById('new-prob-diff')?.value || 'easy',
      description: document.getElementById('new-prob-desc')?.value.trim() || 'Write a solution for this challenge.',
      starter_code: document.getElementById('new-prob-starter')?.value || 'def solution():\n    pass\n',
      test_cases: [
        { call: "solution()", expected_output: "None", description: "Default case" }
      ]
    };

    try {
      await adminApi.createProblem(payload);
      toast.success('Practice problem created successfully!');
      probModal?.classList.add('hidden');
      document.getElementById('form-create-problem')?.reset();
      await loadContent();
    } catch (err) {
      toast.error('Failed to create problem: ' + err.message);
    } finally {
      saveBtn.disabled = false;
      saveBtn.innerHTML = '<span>Save Practice Problem</span>';
    }
  });

  // Handle question form submit
  document.getElementById('form-create-question')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const saveBtn = document.getElementById('btn-save-question');
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<span class="spinner" style="width:14px;height:14px;"></span> Saving...';

    const opts = [
      document.getElementById('new-q-opt-0')?.value.trim(),
      document.getElementById('new-q-opt-1')?.value.trim(),
      document.getElementById('new-q-opt-2')?.value.trim(),
      document.getElementById('new-q-opt-3')?.value.trim(),
    ];

    const payload = {
      text: document.getElementById('new-q-text')?.value.trim(),
      topic_id: parseInt(document.getElementById('new-q-topic')?.value || '1', 10),
      difficulty: document.getElementById('new-q-diff')?.value || 'easy',
      options: opts,
      correct_answer: document.getElementById('new-q-correct')?.value || '0',
    };

    try {
      await adminApi.createQuestion(payload);
      toast.success('Assessment question created successfully!');
      qModal?.classList.add('hidden');
      document.getElementById('form-create-question')?.reset();
      await loadContent();
    } catch (err) {
      toast.error('Failed to create question: ' + err.message);
    } finally {
      saveBtn.disabled = false;
      saveBtn.innerHTML = '<span>Save Assessment Question</span>';
    }
  });
}

async function loadContent() {
  const probList = document.getElementById('adm-problems-list');
  const qList = document.getElementById('adm-questions-list');
  if (probList) probList.innerHTML = '<div style="padding:20px;text-align:center;color:var(--text-muted);"><div class="spinner"></div></div>';
  if (qList) qList.innerHTML = '<div style="padding:20px;text-align:center;color:var(--text-muted);"><div class="spinner"></div></div>';

  try {
    const data = await adminApi.getContentItems();
    cachedTopics = data.topics || [];

    // Populate dropdowns
    populateTopicSelect('new-prob-topic', cachedTopics);
    populateTopicSelect('new-q-topic', cachedTopics);

    // Counts
    const probCount = document.getElementById('adm-problems-count');
    const qCount = document.getElementById('adm-questions-count');
    if (probCount) probCount.textContent = (data.problems || []).length;
    if (qCount) qCount.textContent = (data.questions || []).length;

    // Render Problems
    if (probList) {
      if (!data.problems || data.problems.length === 0) {
        probList.innerHTML = '<div style="padding:20px;text-align:center;color:var(--text-muted);font-size:13px;">No practice problems yet.</div>';
      } else {
        probList.innerHTML = data.problems.map(p => `
          <div style="background:var(--bg-elevated);border:1px solid var(--border);border-radius:var(--radius-sm);padding:12px 14px;display:flex;justify-content:space-between;align-items:center;gap:12px;">
            <div style="min-width:0;">
              <div style="font-weight:600;font-size:13px;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${p.title}</div>
              <div style="display:flex;gap:6px;align-items:center;margin-top:4px;">
                <span class="badge ${p.difficulty === 'easy' ? 'badge-beginner' : p.difficulty === 'medium' ? 'badge-intermediate' : 'badge-advanced'}">${p.difficulty}</span>
                <span style="font-size:11px;color:var(--text-muted);">${p.topic_name}</span>
                <span style="font-size:11px;color:var(--text-muted);">• ${p.test_count} tests</span>
              </div>
            </div>
            <button class="btn btn-ghost btn-sm btn-del-prob" data-id="${p.id}" title="Delete problem" style="color:var(--red);padding:4px 8px;">✕</button>
          </div>
        `).join('');

        probList.querySelectorAll('.btn-del-prob').forEach(btn => {
          btn.addEventListener('click', async () => {
            const id = btn.getAttribute('data-id');
            if (confirm(`Delete practice problem #${id}?`)) {
              try {
                await adminApi.deleteProblem(id);
                toast.success('Problem removed');
                loadContent();
              } catch (err) {
                toast.error('Failed to delete: ' + err.message);
              }
            }
          });
        });
      }
    }

    // Render Questions
    if (qList) {
      if (!data.questions || data.questions.length === 0) {
        qList.innerHTML = '<div style="padding:20px;text-align:center;color:var(--text-muted);font-size:13px;">No diagnostic questions yet.</div>';
      } else {
        qList.innerHTML = data.questions.map(q => `
          <div style="background:var(--bg-elevated);border:1px solid var(--border);border-radius:var(--radius-sm);padding:12px 14px;display:flex;justify-content:space-between;align-items:center;gap:12px;">
            <div style="min-width:0;">
              <div style="font-weight:500;font-size:13px;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${q.text}</div>
              <div style="display:flex;gap:6px;align-items:center;margin-top:4px;">
                <span class="badge ${q.difficulty === 'easy' ? 'badge-beginner' : q.difficulty === 'medium' ? 'badge-intermediate' : 'badge-advanced'}">${q.difficulty}</span>
                <span style="font-size:11px;color:var(--text-muted);">${q.topic_name}</span>
              </div>
            </div>
            <button class="btn btn-ghost btn-sm btn-del-q" data-id="${q.id}" title="Delete question" style="color:var(--red);padding:4px 8px;">✕</button>
          </div>
        `).join('');

        qList.querySelectorAll('.btn-del-q').forEach(btn => {
          btn.addEventListener('click', async () => {
            const id = btn.getAttribute('data-id');
            if (confirm(`Delete diagnostic question #${id}?`)) {
              try {
                await adminApi.deleteQuestion(id);
                toast.success('Question removed');
                loadContent();
              } catch (err) {
                toast.error('Failed to delete: ' + err.message);
              }
            }
          });
        });
      }
    }

  } catch (err) {
    toast.error('Failed to load curriculum items: ' + err.message);
  }
}

function populateTopicSelect(elemId, topics) {
  const sel = document.getElementById(elemId);
  if (!sel) return;
  sel.innerHTML = topics.map(t => `<option value="${t.id}">${t.icon || '🐍'} ${t.name}</option>`).join('');
}

