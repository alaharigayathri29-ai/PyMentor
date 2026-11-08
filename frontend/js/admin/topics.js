/**
 * admin/topics.js
 * Admin Curriculum & Assessment Question Manager (Real Multi-Page Application)
 */

import { requireAuth, initLayout, escapeHtml } from '../common.js?v=20261108_v17';
import { adminApi, learningPathApi } from '../api.js?v=20261108_v17';
import { showToast } from '../components/toast.js?v=20261108_v17';
import { capitalize } from '../utils/formatters.js?v=20261108_v17';

let cachedTopics = [];

async function init() {
  const user = await requireAuth({ requireAdmin: true });
  if (!user) return;

  initLayout('admin-topics', user);

  setupQuestionModal();
  await loadTopicsAndQuestions();
}

function setupQuestionModal() {
  const qModal = document.getElementById('modal-create-question');
  const openBtn = document.getElementById('btn-show-add-question');
  const closeBtn = document.getElementById('btn-close-q-modal');
  const cancelBtn = document.getElementById('btn-cancel-q-modal');

  const closeModal = () => {
    if (qModal) {
      qModal.classList.add('hidden');
      qModal.style.display = 'none';
    }
  };
  const openModal = () => {
    if (qModal) {
      qModal.classList.remove('hidden');
      qModal.style.display = 'flex';
    }
  };

  openBtn?.addEventListener('click', openModal);
  closeBtn?.addEventListener('click', closeModal);
  cancelBtn?.addEventListener('click', closeModal);

  qModal?.addEventListener('click', (e) => {
    if (e.target === qModal) closeModal();
  });

  document.getElementById('form-create-question')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const saveBtn = document.getElementById('btn-save-question');
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<span>Saving…</span>';

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
      showToast('Assessment question created successfully!', 'success');
      qModal?.classList.add('hidden');
      document.getElementById('form-create-question')?.reset();
      await loadTopicsAndQuestions();
    } catch (err) {
      showToast(`Failed to create question: ${err.message}`, 'error');
    } finally {
      saveBtn.disabled = false;
      saveBtn.innerHTML = '<span>Save Diagnostic Question</span>';
    }
  });
}

async function loadTopicsAndQuestions() {
  const topicsList = document.getElementById('adm-curriculum-list');
  const qList = document.getElementById('adm-questions-list');
  const qCount = document.getElementById('adm-questions-count');
  const topicSelect = document.getElementById('new-q-topic');

  if (topicsList) topicsList.innerHTML = '<div style="padding:24px;text-align:center;"><div class="spinner"></div></div>';
  if (qList) qList.innerHTML = '<div style="padding:24px;text-align:center;"><div class="spinner"></div></div>';

  try {
    const [content, curric] = await Promise.all([
      adminApi.getContentItems(),
      learningPathApi.curriculum(),
    ]);

    cachedTopics = content.topics || [];
    if (topicSelect) {
      topicSelect.innerHTML = cachedTopics.map(t => `<option value="${t.id}">${escapeHtml(t.name)}</option>`).join('');
    }

    // Render 7-Module Curriculum Overview
    if (topicsList && curric.modules) {
      topicsList.innerHTML = curric.modules.map(m => `
        <div style="background:#F8FAFC;border:1px solid var(--border);border-radius:var(--r-md);padding:14px 16px;margin-bottom:10px;">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <div style="font-weight:700;font-size:14px;color:var(--text-primary);">Module ${m.module_number}: ${escapeHtml(m.module_name)}</div>
            <span class="badge badge-purple" style="font-size:11px;">${(m.topics || []).length} Topics</span>
          </div>
          <div style="font-size:12px;color:var(--text-secondary);margin-top:4px;">
            ${(m.topics || []).map(t => escapeHtml(t.name)).join(' • ')}
          </div>
        </div>
      `).join('');
    }

    // Render Diagnostic MCQs
    const questions = content.questions || [];
    if (qCount) qCount.textContent = questions.length;

    if (qList) {
      if (questions.length === 0) {
        qList.innerHTML = '<div style="padding:24px;text-align:center;color:var(--text-muted);font-size:13px;">No diagnostic questions found.</div>';
        return;
      }

      qList.innerHTML = questions.map(q => `
        <div style="background:#F8FAFC;border:1px solid var(--border);border-radius:var(--r-md);padding:12px 14px;display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <div style="min-width:0;flex:1;padding-right:12px;">
            <div style="font-weight:600;font-size:13px;color:var(--text-primary);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
              ${escapeHtml(q.text)}
            </div>
            <div style="display:flex;gap:6px;align-items:center;margin-top:4px;">
              <span class="badge ${q.difficulty === 'easy' ? 'badge-beginner' : 'badge-intermediate'}">${capitalize(q.difficulty)}</span>
              <span style="font-size:11px;color:var(--text-secondary);">${escapeHtml(q.topic_name)}</span>
            </div>
          </div>
          <button class="btn btn-ghost btn-sm btn-del-q" data-id="${q.id}" style="color:var(--danger);padding:4px 8px;" title="Delete question">✕</button>
        </div>
      `).join('');

      qList.querySelectorAll('.btn-del-q').forEach(btn => {
        btn.addEventListener('click', async () => {
          const id = parseInt(btn.getAttribute('data-id'), 10);
          if (confirm(`Delete diagnostic question #${id}?`)) {
            try {
              await adminApi.deleteQuestion(id);
              showToast('Question deleted', 'info');
              loadTopicsAndQuestions();
            } catch (err) {
              showToast(err.message, 'error');
            }
          }
        });
      });
    }

  } catch (err) {
    showToast(`Failed to load content: ${err.message}`, 'error');
  }
}

init();

