import { adminApi } from './api.js?v=20261108_v17';
import { showToast } from './app.js?v=20261108_v17';

let _contentData = { topics: [], problems: [], questions: [] };
let _activeCreateTab = 'problem'; // 'problem' | 'question' | 'manage'

export async function initAdminCreate() {
  const el = document.getElementById('page-admin-create');
  el.innerHTML = `<div class="page-content"><div class="flex-center" style="height:300px"><div class="loading-spin" style="font-size:32px">⟳</div></div></div>`;
  try {
    _contentData = await adminApi.getContentItems();
    renderAdminCreate();
  } catch (err) {
    el.innerHTML = `<div class="page-content"><div class="alert alert-error">${err.message}</div></div>`;
  }
}

function renderAdminCreate() {
  const topics = _contentData.topics || [];
  const problems = _contentData.problems || [];
  const questions = _contentData.questions || [];

  document.getElementById('page-admin-create').innerHTML = `
    <div class="page-content animate-in admin-create-view" style="max-width:1050px;margin:0 auto;">
      
      <!-- Top Title Header -->
      <div class="section-header" style="flex-wrap:wrap;gap:12px;margin-bottom:20px;">
        <div>
          <div style="display:flex;align-items:center;gap:10px;">
            <span class="badge badge-purple" style="font-size:11px;text-transform:uppercase;">Curriculum Studio</span>
            <span style="font-size:12px;color:var(--green)">● Creator Mode</span>
          </div>
          <h1 class="page-title" style="margin-top:4px;">Curriculum & Content Creator</h1>
          <p class="page-sub">Create new coding practice problems, author assessment questions, and manage platform challenges</p>
        </div>
        <div style="display:flex;gap:10px;">
          <button class="btn btn-secondary btn-sm" onclick="navigateTo('admin')">
            ← Back to Analytics
          </button>
        </div>
      </div>

      <!-- Mode Selection Tabs -->
      <div style="display:flex;gap:10px;margin-bottom:24px;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:12px;">
        <button class="btn ${_activeCreateTab === 'problem' ? 'btn-primary' : 'btn-ghost'} btn-sm" onclick="switchCreateTab('problem')">
          💻 + New Practice Problem
        </button>
        <button class="btn ${_activeCreateTab === 'question' ? 'btn-primary' : 'btn-ghost'} btn-sm" onclick="switchCreateTab('question')">
          🎯 + New Assessment MCQ
        </button>
        <button class="btn ${_activeCreateTab === 'manage' ? 'btn-secondary' : 'btn-ghost'} btn-sm" onclick="switchCreateTab('manage')">
          📋 Manage Curriculum (${problems.length} problems, ${questions.length} questions)
        </button>
      </div>

      <!-- Tab 1: Create Practice Problem -->
      <div id="create-problem-pane" class="${_activeCreateTab === 'problem' ? '' : 'hidden'} card" style="padding:24px;">
        <h3 style="font-size:17px;font-weight:700;margin-bottom:6px;">Create New Coding Problem</h3>
        <p style="font-size:13px;color:var(--text-muted);margin-bottom:20px;">This problem will immediately appear in students' Practice Lab.</p>

        <form id="create-problem-form" onsubmit="handleProblemSubmit(event)" style="display:flex;flex-direction:column;gap:16px;">
          <div style="display:grid;grid-template-columns:2fr 1fr 1fr;gap:14px;">
            <div>
              <label style="font-size:12px;font-weight:600;display:block;margin-bottom:6px;">Problem Title *</label>
              <input type="text" id="prob-title-input" class="input-field" placeholder="e.g. Check Palindrome Word" required style="width:100%;font-size:13px;" />
            </div>
            <div>
              <label style="font-size:12px;font-weight:600;display:block;margin-bottom:6px;">Topic Module *</label>
              <select id="prob-topic-select" class="input-field" style="width:100%;font-size:13px;">
                ${topics.map(t => `<option value="${t.id}">${t.icon || '📚'} ${t.name}</option>`).join('')}
              </select>
            </div>
            <div>
              <label style="font-size:12px;font-weight:600;display:block;margin-bottom:6px;">Difficulty Level</label>
              <select id="prob-diff-select" class="input-field" style="width:100%;font-size:13px;">
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>
          </div>

          <div>
            <label style="font-size:12px;font-weight:600;display:block;margin-bottom:6px;">Problem Description (Markdown Supported) *</label>
            <textarea id="prob-desc-input" class="input-field" rows="4" placeholder="Write the problem statement, inputs, outputs, and constraints..." required style="width:100%;font-size:13px;resize:vertical;"></textarea>
          </div>

          <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">
            <div>
              <label style="font-size:12px;font-weight:600;display:block;margin-bottom:6px;">Starter Code Template</label>
              <textarea id="prob-starter-input" class="input-field" rows="5" placeholder="def solution(s):\n    # Write code here\n    pass" style="width:100%;font-family:'JetBrains Mono',monospace;font-size:12px;"></textarea>
            </div>
            <div>
              <label style="font-size:12px;font-weight:600;display:block;margin-bottom:6px;">Helpful Hints (one per line)</label>
              <textarea id="prob-hints-input" class="input-field" rows="5" placeholder="Consider converting string to lowercase\nUse two pointers or reverse slice [::-1]" style="width:100%;font-size:12px;"></textarea>
            </div>
          </div>

          <div>
            <label style="font-size:12px;font-weight:600;display:block;margin-bottom:6px;">Test Cases (JSON array format) *</label>
            <textarea id="prob-tests-input" class="input-field" rows="4" required style="width:100%;font-family:'JetBrains Mono',monospace;font-size:12px;">[
  {"call": "solution('racecar')", "expected_output": "True", "description": "Odd length palindrome"},
  {"call": "solution('python')", "expected_output": "False", "description": "Non-palindrome word"}
]</textarea>
          </div>

          <div style="display:flex;justify-content:flex-end;gap:10px;margin-top:8px;">
            <button type="submit" class="btn btn-primary" id="btn-save-problem" style="padding:10px 24px;">
              💾 Save Problem to Platform
            </button>
          </div>
        </form>
      </div>

      <!-- Tab 2: Create Assessment MCQ Question -->
      <div id="create-question-pane" class="${_activeCreateTab === 'question' ? '' : 'hidden'} card" style="padding:24px;">
        <h3 style="font-size:17px;font-weight:700;margin-bottom:6px;">Create Diagnostic Assessment Question</h3>
        <p style="font-size:13px;color:var(--text-muted);margin-bottom:20px;">Add high-yield diagnostic questions to calibrate student skill tiers.</p>

        <form id="create-question-form" onsubmit="handleQuestionSubmit(event)" style="display:flex;flex-direction:column;gap:16px;">
          <div style="display:grid;grid-template-columns:2fr 1fr;gap:14px;">
            <div>
              <label style="font-size:12px;font-weight:600;display:block;margin-bottom:6px;">Diagnostic Module *</label>
              <select id="quest-topic-select" class="input-field" style="width:100%;font-size:13px;">
                ${topics.map(t => `<option value="${t.id}">${t.icon || '📚'} ${t.name}</option>`).join('')}
              </select>
            </div>
            <div>
              <label style="font-size:12px;font-weight:600;display:block;margin-bottom:6px;">Difficulty Level</label>
              <select id="quest-diff-select" class="input-field" style="width:100%;font-size:13px;">
                <option value="easy">Easy (Beginner)</option>
                <option value="medium">Medium (Intermediate)</option>
                <option value="hard">Hard (Advanced)</option>
              </select>
            </div>
          </div>

          <div>
            <label style="font-size:12px;font-weight:600;display:block;margin-bottom:6px;">Question Text / Code Snippet *</label>
            <textarea id="quest-text-input" class="input-field" rows="3" placeholder="What is the output of print(2 ** 3) in Python?" required style="width:100%;font-size:13px;"></textarea>
          </div>

          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div>
              <label style="font-size:12px;font-weight:600;display:block;margin-bottom:4px;">Option A *</label>
              <input type="text" id="quest-opt-0" class="input-field" placeholder="6" required style="width:100%;font-size:13px;" />
            </div>
            <div>
              <label style="font-size:12px;font-weight:600;display:block;margin-bottom:4px;">Option B *</label>
              <input type="text" id="quest-opt-1" class="input-field" placeholder="8" required style="width:100%;font-size:13px;" />
            </div>
            <div>
              <label style="font-size:12px;font-weight:600;display:block;margin-bottom:4px;">Option C *</label>
              <input type="text" id="quest-opt-2" class="input-field" placeholder="9" required style="width:100%;font-size:13px;" />
            </div>
            <div>
              <label style="font-size:12px;font-weight:600;display:block;margin-bottom:4px;">Option D *</label>
              <input type="text" id="quest-opt-3" class="input-field" placeholder="Error" required style="width:100%;font-size:13px;" />
            </div>
          </div>

          <div style="display:grid;grid-template-columns:1fr 2fr;gap:14px;">
            <div>
              <label style="font-size:12px;font-weight:600;display:block;margin-bottom:6px;">Correct Answer Key *</label>
              <select id="quest-correct-select" class="input-field" style="width:100%;font-size:13px;">
                <option value="0">Option A</option>
                <option value="1" selected>Option B</option>
                <option value="2">Option C</option>
                <option value="3">Option D</option>
              </select>
            </div>
            <div>
              <label style="font-size:12px;font-weight:600;display:block;margin-bottom:6px;">Educational Explanation</label>
              <input type="text" id="quest-exp-input" class="input-field" placeholder="** is the exponentiation operator in Python. 2 cubed equals 8." style="width:100%;font-size:13px;" />
            </div>
          </div>

          <div style="display:flex;justify-content:flex-end;gap:10px;margin-top:8px;">
            <button type="submit" class="btn btn-primary" id="btn-save-question" style="padding:10px 24px;">
              💾 Save Question to Assessment
            </button>
          </div>
        </form>
      </div>

      <!-- Tab 3: Manage Existing Curriculum -->
      <div id="manage-curriculum-pane" class="${_activeCreateTab === 'manage' ? '' : 'hidden'}">
        <div class="card" style="padding:20px;margin-bottom:20px;">
          <h3 style="font-size:16px;font-weight:700;margin-bottom:14px;">Existing Practice Problems (${problems.length})</h3>
          <div class="table-wrap">
            <table class="data-table" style="font-size:13px;">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Topic</th>
                  <th>Difficulty</th>
                  <th>Tests</th>
                  <th style="text-align:right">Action</th>
                </tr>
              </thead>
              <tbody>
                ${problems.map(p => `
                  <tr>
                    <td><strong>${p.title}</strong></td>
                    <td style="color:var(--text-accent)">${p.topic_name}</td>
                    <td><span class="badge ${p.difficulty==='easy'?'badge-green':p.difficulty==='medium'?'badge-amber':'badge-red'}">${p.difficulty}</span></td>
                    <td style="color:var(--text-muted)">${p.test_count} cases</td>
                    <td style="text-align:right">
                      <button class="btn btn-danger btn-sm" onclick="deleteProblemItem(${p.id})" style="padding:3px 8px;font-size:11px;">🗑️ Delete</button>
                    </td>
                  </tr>`).join('')}
              </tbody>
            </table>
          </div>
        </div>

        <div class="card" style="padding:20px;">
          <h3 style="font-size:16px;font-weight:700;margin-bottom:14px;">Existing Assessment Questions (${questions.length})</h3>
          <div class="table-wrap">
            <table class="data-table" style="font-size:13px;">
              <thead>
                <tr>
                  <th>Question Snippet</th>
                  <th>Topic</th>
                  <th>Difficulty</th>
                  <th style="text-align:right">Action</th>
                </tr>
              </thead>
              <tbody>
                ${questions.map(q => `
                  <tr>
                    <td style="max-width:380px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${q.text}</td>
                    <td style="color:var(--text-accent)">${q.topic_name}</td>
                    <td><span class="badge ${q.difficulty==='easy'?'badge-green':'badge-amber'}">${q.difficulty}</span></td>
                    <td style="text-align:right">
                      <button class="btn btn-danger btn-sm" onclick="deleteQuestionItem(${q.id})" style="padding:3px 8px;font-size:11px;">🗑️ Delete</button>
                    </td>
                  </tr>`).join('')}
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </div>`;

  setupAdminCreateHandlers();
}

function setupAdminCreateHandlers() {
  window.switchCreateTab = (tab) => {
    _activeCreateTab = tab;
    renderAdminCreate();
  };

  window.handleProblemSubmit = async (e) => {
    e.preventDefault();
    const btn = document.getElementById('btn-save-problem');
    btn.disabled = true;
    btn.textContent = 'Saving Problem...';

    try {
      let testCases = [];
      try {
        testCases = JSON.parse(document.getElementById('prob-tests-input').value.trim());
      } catch (err) {
        throw new Error('Test cases must be valid JSON: ' + err.message);
      }

      const hints = document.getElementById('prob-hints-input').value
        .split('\n')
        .map(h => h.trim())
        .filter(Boolean);

      const payload = {
        title: document.getElementById('prob-title-input').value.trim(),
        topic_id: parseInt(document.getElementById('prob-topic-select').value),
        difficulty: document.getElementById('prob-diff-select').value,
        description: document.getElementById('prob-desc-input').value.trim(),
        starter_code: document.getElementById('prob-starter-input').value,
        test_cases: testCases,
        hints: hints,
      };

      await adminApi.createProblem(payload);
      showToast('Practice problem created and published to students!', 'success');
      _contentData = await adminApi.getContentItems();
      _activeCreateTab = 'manage';
      renderAdminCreate();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      btn.disabled = false;
      btn.textContent = '💾 Save Problem to Platform';
    }
  };

  window.handleQuestionSubmit = async (e) => {
    e.preventDefault();
    const btn = document.getElementById('btn-save-question');
    btn.disabled = true;
    btn.textContent = 'Saving Question...';

    try {
      const opts = [
        document.getElementById('quest-opt-0').value.trim(),
        document.getElementById('quest-opt-1').value.trim(),
        document.getElementById('quest-opt-2').value.trim(),
        document.getElementById('quest-opt-3').value.trim(),
      ];

      const payload = {
        topic_id: parseInt(document.getElementById('quest-topic-select').value),
        difficulty: document.getElementById('quest-diff-select').value,
        text: document.getElementById('quest-text-input').value.trim(),
        options: opts,
        correct_answer: document.getElementById('quest-correct-select').value,
        explanation: document.getElementById('quest-exp-input').value.trim(),
      };

      await adminApi.createQuestion(payload);
      showToast('Assessment question published!', 'success');
      _contentData = await adminApi.getContentItems();
      _activeCreateTab = 'manage';
      renderAdminCreate();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      btn.disabled = false;
      btn.textContent = '💾 Save Question to Assessment';
    }
  };

  window.deleteProblemItem = async (id) => {
    if (!confirm('Are you sure you want to delete this problem?')) return;
    try {
      await adminApi.deleteProblem(id);
      showToast('Problem deleted', 'info');
      _contentData = await adminApi.getContentItems();
      renderAdminCreate();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  window.deleteQuestionItem = async (id) => {
    if (!confirm('Are you sure you want to delete this question?')) return;
    try {
      await adminApi.deleteQuestion(id);
      showToast('Question deleted', 'info');
      _contentData = await adminApi.getContentItems();
      renderAdminCreate();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };
}
