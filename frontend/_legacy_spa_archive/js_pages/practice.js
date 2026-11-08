/**
 * Code Practice Lab Controller.
 * Structured coding exercises with split-screen ByteXL layout and automated test harnesses.
 */

import { practiceApi } from '../api.js';
import { createCodeEditor } from '../components/editor.js';
import { renderMarkdown } from '../utils/markdown.js';
import { showToast } from '../components/toast.js';
import { capitalize, formatRelative } from '../utils/formatters.js';

let editor = null;
let currentProblem = null;
let allProblems = [];
let revealedHintsCount = 0;
let lastResults = null;

export async function initPractice() {
  const mountEl = document.getElementById('practice-editor-mount');
  const probSelect = document.getElementById('prac-problem-select');
  const runSampleBtn = document.getElementById('btn-run-sample');
  const submitBtn = document.getElementById('btn-submit-solution');
  const resetBtn = document.getElementById('btn-reset-starter');
  const tabDesc = document.getElementById('tab-prob-desc');
  const tabSubs = document.getElementById('tab-prob-subs');
  const tabHints = document.getElementById('tab-prob-hints');
  const paneDesc = document.getElementById('pane-prob-desc');
  const paneSubs = document.getElementById('pane-prob-subs');
  const paneHints = document.getElementById('pane-prob-hints');
  const revealHintBtn = document.getElementById('btn-reveal-hint');

  // Load problems (filter by session topic if set)
  try {
    const topicId = sessionStorage.getItem('practice_topic_id');
    allProblems = topicId
      ? await practiceApi.problems(topicId)
      : await practiceApi.recommended();

    if (!allProblems || allProblems.length === 0) {
      allProblems = await practiceApi.problems();
    }

    if (allProblems.length === 0) {
      showToast('No practice problems found.', 'info');
      return;
    }

    // Populate problem switcher
    if (probSelect) {
      probSelect.innerHTML = allProblems.map(p => `
        <option value="${p.id}">${escapeHtml(p.title)} (${capitalize(p.difficulty)})</option>
      `).join('');

      probSelect.addEventListener('change', (e) => {
        const selId = parseInt(e.target.value, 10);
        const prob = allProblems.find(p => p.id === selId);
        if (prob) selectProblem(prob);
      });
    }

    // Tabs logic
    const switchTab = (activeTab, activePane) => {
      [tabDesc, tabSubs, tabHints].forEach(t => t?.classList.remove('active'));
      [paneDesc, paneSubs, paneHints].forEach(p => p?.classList.add('hidden'));
      activeTab?.classList.add('active');
      activePane?.classList.remove('hidden');
    };

    tabDesc?.addEventListener('click', () => switchTab(tabDesc, paneDesc));
    tabSubs?.addEventListener('click', () => {
      switchTab(tabSubs, paneSubs);
      loadProblemSubmissions(currentProblem?.id);
    });
    tabHints?.addEventListener('click', () => switchTab(tabHints, paneHints));

    // Reveal next hint
    revealHintBtn?.addEventListener('click', () => {
      if (!currentProblem || !currentProblem.hints) return;
      const totalHints = currentProblem.hints.length;
      if (revealedHintsCount < totalHints) {
        revealedHintsCount++;
        renderHints();
      } else {
        showToast('All available hints revealed!', 'info');
      }
    });

    // Reset Starter
    resetBtn?.addEventListener('click', () => {
      if (editor && currentProblem) {
        editor.setValue(currentProblem.starter_code || '# Write your solution here\n');
        showToast('Starter code restored.', 'info');
      }
    });

    // Run Sample Tests
    runSampleBtn?.addEventListener('click', () => evaluateSolution(false));

    // Submit Solution
    submitBtn?.addEventListener('click', () => evaluateSolution(true));

    // Select first problem
    selectProblem(allProblems[0]);

  } catch (err) {
    showToast(`Error loading practice lab: ${err.message}`, 'error');
  }
}

function selectProblem(problem) {
  currentProblem = problem;
  revealedHintsCount = 0;
  lastResults = null;

  const titleEl = document.getElementById('prac-prob-title');
  const diffEl = document.getElementById('prac-prob-diff');
  const topicEl = document.getElementById('prac-prob-topic');
  const bodyEl = document.getElementById('prac-prob-body');
  const constraintsEl = document.getElementById('prac-prob-constraints');
  const hintsCountEl = document.getElementById('prac-hints-count');
  const mountEl = document.getElementById('practice-editor-mount');
  const diffPane = document.getElementById('prac-test-diff-view');
  const pillsList = document.getElementById('prac-test-pills');
  const runBadge = document.getElementById('prac-run-badge');
  const scoreSummary = document.getElementById('prac-score-summary');

  if (titleEl) titleEl.textContent = problem.title;
  if (diffEl) {
    diffEl.textContent = capitalize(problem.difficulty);
    diffEl.className = `badge ${problem.difficulty === 'easy' ? 'badge-green' : (problem.difficulty === 'medium' ? 'badge-amber' : 'badge-red')}`;
  }
  if (topicEl) topicEl.textContent = problem.topic_name || 'Python';
  if (bodyEl) bodyEl.innerHTML = renderMarkdown(problem.description);
  if (constraintsEl) constraintsEl.textContent = problem.constraints || 'Standard execution limits (5.0s, 128 MB)';
  if (hintsCountEl) hintsCountEl.textContent = (problem.hints || []).length;

  // Code editor initialization
  editor = createCodeEditor(mountEl, problem.starter_code || '# Write your solution here\n');

  // Reset hints pane
  renderHints();

  // Reset test console
  if (runBadge) {
    runBadge.textContent = 'Ready';
    runBadge.className = 'badge badge-gray';
  }
  if (scoreSummary) scoreSummary.textContent = '';
  if (pillsList) {
    const samples = problem.sample_cases || [];
    pillsList.innerHTML = samples.map((tc, i) => `
      <div class="test-pill ${i === 0 ? 'active' : ''}" onclick="window.selectTestPill(${i})">Sample Case ${i + 1}</div>
    `).join('') || '<div class="test-pill active">Sample Case 1</div>';
  }

  if (diffPane) {
    const firstSample = (problem.sample_cases || [])[0];
    if (firstSample) {
      diffPane.innerHTML = `
        <div class="test-diff-row">
          <label>Sample Call / Input:</label>
          <div class="test-diff-val"><code>${escapeHtml(firstSample.call || firstSample.input || '')}</code></div>
        </div>
        <div class="test-diff-row">
          <label>Expected Output:</label>
          <div class="test-diff-val"><code>${escapeHtml(firstSample.expected_output || '')}</code></div>
        </div>
      `;
    } else {
      diffPane.innerHTML = '<div style="color:var(--text-muted);">Click "Run Sample Tests" to run sample evaluation.</div>';
    }
  }

  window.selectTestPill = (idx) => {
    document.querySelectorAll('.test-pill').forEach((p, i) => {
      p.classList.toggle('active', i === idx);
    });
    if (lastResults && lastResults.results && lastResults.results[idx]) {
      renderTestDetail(lastResults.results[idx]);
    } else if (problem.sample_cases && problem.sample_cases[idx]) {
      const tc = problem.sample_cases[idx];
      if (diffPane) {
        diffPane.innerHTML = `
          <div class="test-diff-row">
            <label>Sample Call / Input:</label>
            <div class="test-diff-val"><code>${escapeHtml(tc.call || tc.input || '')}</code></div>
          </div>
          <div class="test-diff-row">
            <label>Expected Output:</label>
            <div class="test-diff-val"><code>${escapeHtml(tc.expected_output || '')}</code></div>
          </div>
        `;
      }
    }
  };
}

function renderHints() {
  const container = document.getElementById('prac-revealed-hints');
  if (!container || !currentProblem) return;
  const hints = currentProblem.hints || [];

  if (revealedHintsCount === 0) {
    container.innerHTML = '<div style="font-size:12px;color:var(--text-muted);padding:6px 0;">Click "Reveal Next Hint" above to unlock guidance without giving away the full answer.</div>';
    return;
  }

  container.innerHTML = hints.slice(0, revealedHintsCount).map((h, i) => `
    <div style="padding:10px 14px;background:rgba(124,58,237,0.1);border:1px solid rgba(124,58,237,0.25);border-radius:8px;font-size:13px;color:#cbd5e1;">
      <strong style="color:var(--text-accent);">💡 Hint ${i + 1}:</strong> ${escapeHtml(h)}
    </div>
  `).join('');
}

async function evaluateSolution(isFinalSubmit = false) {
  if (!editor || !currentProblem) return;
  const code = editor.getValue();
  const runSampleBtn = document.getElementById('btn-run-sample');
  const submitBtn = document.getElementById('btn-submit-solution');
  const runBadge = document.getElementById('prac-run-badge');
  const scoreSummary = document.getElementById('prac-score-summary');
  const pillsList = document.getElementById('prac-test-pills');

  const activeBtn = isFinalSubmit ? submitBtn : runSampleBtn;
  if (activeBtn) {
    activeBtn.disabled = true;
    activeBtn.innerHTML = `<span>Evaluating…</span>`;
  }
  if (runBadge) {
    runBadge.textContent = isFinalSubmit ? 'Submitting…' : 'Testing…';
    runBadge.className = 'badge badge-blue';
  }

  try {
    const res = isFinalSubmit
      ? await practiceApi.submit(currentProblem.id, code)
      : await practiceApi.testRun(currentProblem.id, code);

    lastResults = res;

    // Badges update
    const passed = res.passed || 0;
    const total = res.total || 0;
    const score = Math.round(res.score || 0);

    if (runBadge) {
      if (passed === total) {
        runBadge.textContent = `All Tests Passed (${passed}/${total})`;
        runBadge.className = 'badge badge-green';
      } else {
        runBadge.textContent = `${passed}/${total} Passed (${score}%)`;
        runBadge.className = 'badge badge-red';
      }
    }

    if (scoreSummary) {
      scoreSummary.textContent = isFinalSubmit
        ? `Submission Score: ${score}% • ${passed === total ? 'Mastery Updated! +75 XP' : 'Keep trying!'}`
        : `Sample Run: ${passed}/${total} cases satisfied`;
    }

    // Render test case pills
    const cases = res.results || [];
    if (pillsList && cases.length > 0) {
      pillsList.innerHTML = cases.map((c, i) => `
        <div class="test-pill ${i === 0 ? 'active' : ''} ${c.passed ? 'passed' : 'failed'}" onclick="window.selectTestPill(${i})">
          ${c.passed ? '✓' : '✗'} Case ${i + 1}
        </div>
      `).join('');
      renderTestDetail(cases[0]);
    }

    if (isFinalSubmit) {
      if (passed === total) {
        showToast('🎉 Perfect! All test cases passed. Submission recorded!', 'success');
      } else {
        showToast(`Submission evaluated: ${passed}/${total} test cases passed.`, 'warn');
      }
    }

  } catch (err) {
    if (runBadge) {
      runBadge.textContent = 'Error';
      runBadge.className = 'badge badge-red';
    }
    showToast(err.message, 'error');
  } finally {
    if (activeBtn) {
      activeBtn.disabled = false;
      activeBtn.innerHTML = isFinalSubmit ? '<span>🏆 Submit Solution</span>' : '<span>▶ Run Sample Tests</span>';
    }
  }
}

function renderTestDetail(testCase) {
  const diffPane = document.getElementById('prac-test-diff-view');
  if (!diffPane || !testCase) return;

  const isPassed = testCase.passed;
  diffPane.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
      <span style="font-weight:700;font-size:13px;color:#fff;">${escapeHtml(testCase.description || 'Test Case')}</span>
      <span class="badge ${isPassed ? 'badge-green' : 'badge-red'}">${isPassed ? 'PASSED ✓' : 'FAILED ✗'}</span>
    </div>
    
    <div class="test-diff-row">
      <label>Expected Output:</label>
      <div class="test-diff-val" style="color:#4ade80;"><code>${escapeHtml(testCase.expected || '')}</code></div>
    </div>

    <div class="test-diff-row">
      <label>Actual Output:</label>
      <div class="test-diff-val" style="color:${isPassed ? '#4ade80' : '#f87171'};"><code>${escapeHtml(testCase.actual || testCase.error || '(no output)')}</code></div>
    </div>

    ${testCase.error ? `
      <div class="test-diff-row">
        <label>Error / Traceback:</label>
        <div class="test-diff-val" style="color:#f87171;font-size:11.5px;"><code>${escapeHtml(testCase.error)}</code></div>
      </div>
    ` : ''}

    ${testCase.stdout ? `
      <div class="test-diff-row">
        <label>Your Stdout (print statements):</label>
        <div class="test-diff-val" style="color:#94a3b8;font-size:11.5px;"><code>${escapeHtml(testCase.stdout)}</code></div>
      </div>
    ` : ''}
  `;
}

async function loadProblemSubmissions(problemId) {
  const listEl = document.getElementById('prac-subs-list');
  if (!listEl || !problemId) return;

  listEl.innerHTML = `<div class="flex-center" style="padding:16px;"><div class="loading-spin">⟳</div></div>`;

  try {
    const subs = await practiceApi.mySubmissions(problemId);
    if (!subs || subs.length === 0) {
      listEl.innerHTML = '<div style="font-size:12px;color:var(--text-muted);padding:12px 0;">No submissions recorded for this problem yet.</div>';
      return;
    }

    listEl.innerHTML = subs.map(s => `
      <div style="padding:10px 14px;background:rgba(255,255,255,0.02);border:1px solid var(--border);border-radius:8px;display:flex;justify-content:space-between;align-items:center;">
        <div>
          <span class="badge ${s.score >= 70 ? 'badge-green' : 'badge-red'}">${s.passed_cases}/${s.total_cases} Passed (${Math.round(s.score)}%)</span>
          <div style="font-size:11px;color:var(--text-muted);margin-top:4px;">${formatRelative(s.submitted_at)}</div>
        </div>
        <button class="btn btn-ghost btn-sm" onclick="window.restoreSubmissionCode('${btoa(unescape(encodeURIComponent(s.code || '')))}')">
          Load Code
        </button>
      </div>
    `).join('');

    window.restoreSubmissionCode = (b64Code) => {
      try {
        const decoded = decodeURIComponent(escape(atob(b64Code)));
        if (editor) {
          editor.setValue(decoded);
          showToast('Loaded past submission code into editor.', 'info');
        }
      } catch (e) {
        showToast('Failed to load code snippet', 'error');
      }
    };

  } catch (err) {
    listEl.innerHTML = `<div class="alert alert-error">${err.message}</div>`;
  }
}

function escapeHtml(str) {
  return (str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

