/**
 * practice.js — Topic-Wise 50 Problems & Dual-View Practice Workspace
 * Real Multi-Topic Engine · Topic Labs Catalog (Image 2) · ByteXL IDE Workspace (Image 3)
 */

import { requireAuth, initLayout, escapeHtml } from './common.js?v=20261108_v18';
import { practiceApi, learningPathApi } from './api.js?v=20261108_v18';
import { showToast } from './components/toast.js?v=20261108_v18';
import { capitalize } from './utils/formatters.js?v=20261108_v18';

const LANG_TEMPLATES = {
  python: {
    mode: 'python',
    file: 'main.py',
    icon: '🐍',
    template: (p) => p?.starter_code || '# Write your Python solution here\n'
  },
  c: {
    mode: 'text/x-csrc',
    file: 'solution.c',
    icon: '⚙️',
    template: (p) => `// C (GCC) Practice Solution\n#include <stdio.h>\n#include <stdlib.h>\n\nint main() {\n    printf("Running C Solution for: ${p?.title || 'Practice Challenge'}\\n");\n    return 0;\n}\n`
  },
  cpp: {
    mode: 'text/x-c++src',
    file: 'solution.cpp',
    icon: '⚡',
    template: (p) => `// Modern C++ (G++)\n#include <iostream>\n#include <vector>\n#include <numeric>\n\nint main() {\n    std::cout << "Running C++ Solution for: ${p?.title || 'Practice Challenge'}" << std::endl;\n    return 0;\n}\n`
  },
  java: {
    mode: 'text/x-java',
    file: 'Solution.java',
    icon: '☕',
    template: (p) => `// Enterprise Java 21\npublic class Solution {\n    public static void main(String[] args) {\n        System.out.println("Running Java Solution for: ${p?.title || 'Practice Challenge'}");\n    }\n}\n`
  }
};

let editor = null;
let topicsList = [];
let currentTopic = null;
let currentProblems = [];
let currentProblem = null;
let mySubmissions = [];
let solvedProblemIds = new Set();
let attemptedProblemIds = new Set();
let timerSeconds = 0;
let timerInterval = null;
let revealedHintsCount = 0;

// Topic Icons mapping
const TOPIC_ICONS = {
  'variables': '📦',
  'operators': '🧮',
  'conditions': '⚡',
  'loops': '🔄',
  'functions': '🧩',
  'lists': '📊',
  'dictionaries': '🗂️',
  'strings': '🔤',
  'comprehensions': '💡',
  'error-handling': '🛡️',
  'file-io': '📁',
  'oop': '🏛️',
  'modules': '📦',
  'practical-python': '🚀',
};

async function init() {
  const user = await requireAuth();
  if (!user) return;

  initLayout('practice', user);

  // Initialize CodeMirror editor
  initEditor();

  // Load user submissions to calculate checkmarks (✓ / ✗)
  try {
    const subs = await practiceApi.mySubmissions().catch(() => []);
    mySubmissions = subs;
    subs.forEach(s => {
      attemptedProblemIds.add(s.problem_id);
      if (s.score >= 70) {
        solvedProblemIds.add(s.problem_id);
      }
    });
  } catch (err) {
    console.warn('[Practice] Submissions load error:', err);
  }

  // Load topics
  await loadTopics();

  // Setup UI event listeners
  setupViewToggles();
  setupCatalogFilters();
  setupWorkspaceActions();
  startTimer();
}

/* ── 1. CodeMirror Editor Initialization ───────────────────────────────────── */
function initEditor() {
  const mount = document.getElementById('workspace-editor-mount');
  if (!mount) return;

  if (window.CodeMirror) {
    editor = window.CodeMirror(mount, {
      value: '# Write your Python code here\n',
      mode: 'python',
      theme: 'dracula',
      lineNumbers: true,
      indentUnit: 4,
      tabSize: 4,
      indentWithTabs: false,
      lineWrapping: true,
      matchBrackets: true,
      autoCloseBrackets: true,
    });

    // Auto-save student draft as they type
    editor.on('change', () => {
      if (currentProblem) {
        localStorage.setItem(`pym_practice_draft_${currentProblem.id}`, editor.getValue());
      }
    });
  } else {
    // Fallback textarea if CDN fails
    mount.innerHTML = '<textarea id="fallback-code-area" style="width:100%;height:100%;background:#2C1A0E;color:#FFF8F0;font-family:monospace;padding:16px;border:none;outline:none;font-size:14px;resize:none;"></textarea>';
    const area = document.getElementById('fallback-code-area');
    editor = {
      getValue: () => area.value,
      setValue: (val) => { area.value = val; },
    };
    area.addEventListener('input', () => {
      if (currentProblem) {
        localStorage.setItem(`pym_practice_draft_${currentProblem.id}`, area.value);
      }
    });
  }
}

/* ── 2. Load Topics & Render Top Strip ─────────────────────────────────────── */
async function loadTopics() {
  const strip = document.getElementById('topic-pills-strip');
  if (!strip) return;

  try {
    const curriculum = await learningPathApi.curriculum().catch(() => ({ modules: [] }));
    const extracted = [];

    // Extract all topics from curriculum modules
    (curriculum.modules || []).forEach(m => {
      (m.topics || []).forEach(t => {
        extracted.push({
          id: t.id,
          name: t.name,
          slug: t.slug,
          icon: TOPIC_ICONS[t.slug] || t.icon || '📚',
        });
      });
    });

    topicsList = extracted.length > 0 ? extracted : [
      { id: 1, name: 'Variables & Data Types', slug: 'variables', icon: '📦' },
      { id: 2, name: 'Operators & Expressions', slug: 'operators', icon: '🧮' },
      { id: 3, name: 'Conditional Statements', slug: 'conditions', icon: '⚡' },
      { id: 4, name: 'Loops', slug: 'loops', icon: '🔄' },
      { id: 5, name: 'Functions', slug: 'functions', icon: '🧩' },
      { id: 6, name: 'Lists & Tuples', slug: 'lists', icon: '📊' },
      { id: 7, name: 'Dictionaries & Sets', slug: 'dictionaries', icon: '🗂️' },
      { id: 8, name: 'String Operations', slug: 'strings', icon: '🔤' },
      { id: 9, name: 'List Comprehensions', slug: 'comprehensions', icon: '💡' },
      { id: 10, name: 'Error Handling', slug: 'error-handling', icon: '🛡️' },
      { id: 11, name: 'File I/O', slug: 'file-io', icon: '📁' },
      { id: 12, name: 'Object-Oriented Programming', slug: 'oop', icon: '🏛️' },
      { id: 13, name: 'Modules & Packages', slug: 'modules', icon: '📦' },
      { id: 14, name: 'Problem Solving & Projects', slug: 'practical-python', icon: '🚀' },
    ];

    // Check URL topic_id parameter
    const urlParams = new URLSearchParams(window.location.search);
    const paramTopicId = urlParams.get('topic_id') ? parseInt(urlParams.get('topic_id'), 10) : null;
    const initialTopic = topicsList.find(t => t.id === paramTopicId) || topicsList[0];

    // Render Pills
    strip.innerHTML = topicsList.map(t => `
      <div class="topic-nav-pill ${t.id === initialTopic.id ? 'active' : ''}" data-topic-id="${t.id}">
        <span>${t.icon}</span>
        <span>${escapeHtml(t.name)}</span>
        <span class="pill-count">50</span>
      </div>
    `).join('');

    // Attach click listener to each pill
    strip.querySelectorAll('.topic-nav-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        const tid = parseInt(pill.getAttribute('data-topic-id'), 10);
        const selected = topicsList.find(t => t.id === tid);
        if (selected) selectTopic(selected);
      });
    });

    selectTopic(initialTopic);
  } catch (err) {
    console.error('[Practice] Topics error:', err);
  }
}

/* ── 3. Select Topic & Load its 50 Problems ────────────────────────────────── */
async function selectTopic(topic) {
  currentTopic = topic;
  catalogCurrentPage = 1;

  // Highlight active pill
  document.querySelectorAll('.topic-nav-pill').forEach(pill => {
    pill.classList.toggle('active', parseInt(pill.getAttribute('data-topic-id'), 10) === topic.id);
  });

  // Update headers
  set('current-topic-label', `${topic.icon} ${topic.name}`);
  set('catalog-heading', `${topic.name} Labs`);
  set('catalog-subheading', `Practice lab exercises on ${topic.name}. Select any challenge to code and test run.`);

  // Load 50 problems for this topic
  try {
    const problems = await practiceApi.problems(topic.id);
    currentProblems = problems;

    const solvedCount = problems.filter(p => solvedProblemIds.has(p.id)).length;
    set('topic-problem-counter', `${problems.length} Problems`);
    set('topic-solved-counter', `${solvedCount} Solved`);
    set('sidebar-prob-count', problems.length);

    // Render View 1 (Catalog Table) and View 2 (Sidebar List)
    renderCatalogTable(problems);
    renderSidebarList(problems);

    // If problem_id in URL, select that problem; else select first problem
    const urlParams = new URLSearchParams(window.location.search);
    const paramProbId = urlParams.get('problem_id') ? parseInt(urlParams.get('problem_id'), 10) : null;
    const targetProblem = problems.find(p => p.id === paramProbId) || problems[0];

    if (targetProblem) {
      loadProblemIntoWorkspace(targetProblem);
    }
  } catch (err) {
    console.error('[Practice] Load problems error:', err);
    showToast('Could not load problems for topic', 'error');
  }
}

let catalogCurrentPage = 1;
const CATALOG_PAGE_SIZE = 10;
let currentFilteredProblems = [];

/* ── 4. Render VIEW 1: Topic Labs Catalog Table with 10 Per Page Pagination ─── */
function renderCatalogTable(problems) {
  const tbody = document.getElementById('catalog-table-body');
  if (!tbody) return;

  if (problems) {
    currentFilteredProblems = problems;
  }

  const totalItems = currentFilteredProblems.length;
  const totalPages = Math.max(1, Math.ceil(totalItems / CATALOG_PAGE_SIZE));

  if (catalogCurrentPage > totalPages) catalogCurrentPage = totalPages;
  if (catalogCurrentPage < 1) catalogCurrentPage = 1;

  const startIdx = (catalogCurrentPage - 1) * CATALOG_PAGE_SIZE;
  const endIdx = Math.min(startIdx + CATALOG_PAGE_SIZE, totalItems);
  const pageProblems = currentFilteredProblems.slice(startIdx, endIdx);

  if (!pageProblems || pageProblems.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:40px;color:#A07050;">No problems found matching this filter.</td></tr>';
  } else {
    tbody.innerHTML = pageProblems.map(p => {
      const isSolved = solvedProblemIds.has(p.id);
      const isAttempted = attemptedProblemIds.has(p.id);

      const statusBadge = isSolved
        ? '<span class="status-badge-icon passed" title="Solved">✓</span>'
        : isAttempted
        ? '<span class="status-badge-icon failed" title="Attempted">✗</span>'
        : '<span class="status-badge-icon unsolved" title="Unsolved">○</span>';

      const diffClass = p.difficulty === 'hard' ? 'badge-rose' : p.difficulty === 'medium' ? 'badge-amber' : 'badge-teal';
      const cleanDesc = (p.description || '').replace(/[#*`]/g, '').slice(0, 110) + '…';

      return `
        <tr>
          <td style="text-align:center;">${statusBadge}</td>
          <td>
            <div class="lab-title-cell">
              <span>${escapeHtml(p.title)}</span>
            </div>
          </td>
          <td><span class="badge ${diffClass}">${capitalize(p.difficulty)}</span></td>
          <td><div class="lab-desc-cell">${escapeHtml(cleanDesc)}</div></td>
          <td style="text-align:right;">
            <button class="btn-open-lab" data-problem-id="${p.id}" title="Open single-problem workspace">
              Open
            </button>
          </td>
        </tr>
      `;
    }).join('');
  }

  // Update Pagination Controls
  const infoText = document.getElementById('pagination-info-text');
  if (infoText) {
    infoText.textContent = totalItems === 0
      ? 'No problems found'
      : `Showing ${startIdx + 1}–${endIdx} of ${totalItems} problems`;
  }

  const prevBtn = document.getElementById('btn-page-prev');
  if (prevBtn) {
    prevBtn.disabled = catalogCurrentPage <= 1;
  }

  const nextBtn = document.getElementById('btn-page-next');
  if (nextBtn) {
    nextBtn.disabled = catalogCurrentPage >= totalPages;
  }

  const pageContainer = document.getElementById('page-numbers-container');
  if (pageContainer) {
    let pagesHtml = '';
    for (let i = 1; i <= totalPages; i++) {
      pagesHtml += `<button class="page-num-btn ${i === catalogCurrentPage ? 'active' : ''}" data-page="${i}">${i}</button>`;
    }
    pageContainer.innerHTML = pagesHtml;
    pageContainer.querySelectorAll('.page-num-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        catalogCurrentPage = parseInt(btn.getAttribute('data-page'), 10);
        renderCatalogTable();
      });
    });
  }

  // Attach click to each "Open" button -> opens only this ONE problem in workspace
  tbody.querySelectorAll('.btn-open-lab').forEach(btn => {
    btn.addEventListener('click', () => {
      const pid = parseInt(btn.getAttribute('data-problem-id'), 10);
      const prob = currentProblems.find(p => p.id === pid);
      if (prob) {
        loadProblemIntoWorkspace(prob);
        switchToWorkspaceView();
      }
    });
  });
}

/* ── 5. Render VIEW 2: Workspace Problems Sidebar (Reference Image 3) ──────── */
function renderSidebarList(problems) {
  const container = document.getElementById('sidebar-problems-list');
  if (!container) return;

  container.innerHTML = problems.map((p, idx) => {
    const isSolved = solvedProblemIds.has(p.id);
    const isAttempted = attemptedProblemIds.has(p.id);

    const icon = isSolved
      ? '<span class="status-badge-icon passed">✓</span>'
      : isAttempted
      ? '<span class="status-badge-icon failed">✗</span>'
      : '<span class="status-badge-icon unsolved">○</span>';

    const isActive = currentProblem && currentProblem.id === p.id;

    return `
      <div class="problem-list-item ${isActive ? 'active' : ''}" data-problem-id="${p.id}">
        <div style="display:flex;align-items:center;gap:8px;min-width:0;flex:1;">
          ${icon}
          <span style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
            ${escapeHtml(p.title)}
          </span>
        </div>
        <span style="font-size:10.5px;color:#94A3B8;text-transform:uppercase;font-weight:700;">
          ${p.difficulty[0]}
        </span>
      </div>
    `;
  }).join('');

  // Attach click listener
  container.querySelectorAll('.problem-list-item').forEach(item => {
    item.addEventListener('click', () => {
      const pid = parseInt(item.getAttribute('data-problem-id'), 10);
      const prob = currentProblems.find(p => p.id === pid);
      if (prob) loadProblemIntoWorkspace(prob);
    });
  });
}

/* ── 6. Load Problem into Editor and Workspace ─────────────────────────────── */
function loadProblemIntoWorkspace(problem) {
  currentProblem = problem;
  revealedHintsCount = 0;

  // Highlight in sidebar
  document.querySelectorAll('.problem-list-item').forEach(item => {
    item.classList.toggle('active', parseInt(item.getAttribute('data-problem-id'), 10) === problem.id);
  });

  // Populate Editor with saved draft / submission if present, else starter code
  const langSelect = document.getElementById('practice-lang-select');
  const currentLang = langSelect ? langSelect.value : 'python';
  const cfg = LANG_TEMPLATES[currentLang] || LANG_TEMPLATES.python;

  const prevSub = mySubmissions.find(s => s.problem_id === problem.id);
  const localDraft = localStorage.getItem(`pym_practice_draft_${problem.id}_${currentLang}`) || (currentLang === 'python' ? localStorage.getItem(`pym_practice_draft_${problem.id}`) : null);
  const codeToLoad = localDraft || prevSub?.code || cfg.template(problem);

  if (editor) {
    if (editor.setOption) editor.setOption('mode', cfg.mode);
    editor.setValue(codeToLoad);
    if (editor.refresh) {
      setTimeout(() => editor.refresh(), 80);
    }
  }

  const fileIcon = document.getElementById('editor-file-icon');
  const fileName = document.getElementById('editor-file-name');
  if (fileIcon) fileIcon.textContent = cfg.icon;
  if (fileName) fileName.textContent = cfg.file;

  // Populate Right Pane Details
  set('ws-problem-title', problem.title);
  set('ws-problem-diff', capitalize(problem.difficulty));
  set('ws-problem-topic', problem.topic_name || currentTopic?.name || 'Python');
  set('ws-problem-desc', problem.description || '');

  const constraintsBox = document.getElementById('ws-problem-constraints');
  if (constraintsBox) {
    constraintsBox.textContent = problem.constraints || 'Time Limit: 5.0s · Memory Limit: 128 MB · Python 3.10+ environment';
  }

  // Populate Past Submissions Tab
  const subsContainer = document.getElementById('ws-submissions-container');
  if (subsContainer) {
    const probSubs = mySubmissions.filter(s => s.problem_id === problem.id);
    if (probSubs.length > 0) {
      subsContainer.innerHTML = probSubs.map((s, idx) => {
        const isPassed = s.score >= 70;
        return `
          <div style="background:#FFFFFF;border:1px solid rgba(200,160,100,0.25);border-radius:10px;padding:12px 16px;margin-bottom:12px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
              <span class="badge ${isPassed ? 'badge-green' : 'badge-rose'}">
                ${isPassed ? '✓ PASSED' : '✗ FAILED'} · Score: ${s.score}%
              </span>
              <button class="btn btn-secondary btn-sm btn-load-past-sub" data-idx="${idx}" style="font-size:11px;padding:3px 8px;">
                ↺ Load Code into Editor
              </button>
            </div>
            <pre style="background:#2C1A0E;color:#FFF8F0;padding:10px;border-radius:6px;font-size:12px;overflow-x:auto;"><code>${escapeHtml(s.code || '')}</code></pre>
          </div>
        `;
      }).join('');

      subsContainer.querySelectorAll('.btn-load-past-sub').forEach(btn => {
        btn.addEventListener('click', () => {
          const idx = parseInt(btn.getAttribute('data-idx'), 10);
          const sub = probSubs[idx];
          if (sub && editor) {
            editor.setValue(sub.code);
            showToast('Loaded past submission code into workspace editor.', 'info');
          }
        });
      });
    } else {
      subsContainer.innerHTML = '<div style="color:#64748B;font-size:13px;padding:12px 0;">No previous submissions recorded for this challenge yet.</div>';
    }
  }

  // Populate Sample Test Cases
  const sampleContainer = document.getElementById('ws-sample-cases-container');
  if (sampleContainer) {
    const samples = problem.sample_cases || [];
    if (samples.length > 0) {
      sampleContainer.innerHTML = samples.map((tc, i) => `
        <div class="sample-case-box">
          <div style="font-weight:700;color:#2563EB;margin-bottom:4px;">Sample Case ${i + 1}</div>
          <div><strong>Call:</strong> <code>${escapeHtml(tc.call || tc.input || '')}</code></div>
          <div><strong>Expected:</strong> <code>${escapeHtml(tc.expected_output || '')}</code></div>
        </div>
      `).join('');
    } else {
      sampleContainer.innerHTML = '<div style="color:#64748B;font-size:12.5px;">Test cases will be evaluated on test run.</div>';
    }
  }

  // Populate All Test Cases Tab
  const allTestsContainer = document.getElementById('ws-all-tests-container');
  if (allTestsContainer) {
    allTestsContainer.innerHTML = `
      <div style="color:#64748B;font-size:13px;line-height:1.6;">
        This challenge evaluates your code against automated test cases covering typical inputs and edge cases.<br>
        Click <strong>"▶ Run Sample Tests"</strong> to verify before submitting.
      </div>
    `;
  }

  // Reset hints
  const hintsCount = (problem.hints || []).length;
  set('ws-hint-count', hintsCount);
  const hintsContainer = document.getElementById('ws-hints-container');
  if (hintsContainer) {
    hintsContainer.innerHTML = '<div style="color:#64748B;font-size:13px;">Click "Reveal Next Hint" below if you need guidance.</div>';
  }

  // Clear evaluation console
  set('eval-console-output', 'Click "Run Sample Tests" or "Submit Solution" to verify your Python code against test suites.');
}

/* ── 7. Workspace Actions: Run Tests, Submit, Reset ────────────────────────── */
function setupWorkspaceActions() {
  const runBtn = document.getElementById('btn-workspace-run');
  const submitBtn = document.getElementById('btn-workspace-submit');
  const resetBtn = document.getElementById('btn-reset-code');
  const revealHintBtn = document.getElementById('btn-ws-reveal-hint');
  const langSelect = document.getElementById('practice-lang-select');

  // Multi-Language Switcher
  langSelect?.addEventListener('change', () => {
    if (!currentProblem || !editor) return;
    const lang = langSelect.value;
    const cfg = LANG_TEMPLATES[lang] || LANG_TEMPLATES.python;

    const fileIcon = document.getElementById('editor-file-icon');
    const fileName = document.getElementById('editor-file-name');
    if (fileIcon) fileIcon.textContent = cfg.icon;
    if (fileName) fileName.textContent = cfg.file;

    if (editor && editor.setOption) {
      editor.setOption('mode', cfg.mode);
    }

    const savedDraft = localStorage.getItem(`pym_practice_draft_${currentProblem.id}_${lang}`);
    if (savedDraft) {
      editor.setValue(savedDraft);
    } else {
      editor.setValue(cfg.template(currentProblem));
    }
    showToast(`Switched workspace environment to ${lang.toUpperCase()}`, 'info');
  });

  // Run Sample Tests
  runBtn?.addEventListener('click', async () => {
    if (!currentProblem || !editor) return;
    const code = editor.getValue();
    const lang = langSelect ? langSelect.value : 'python';

    runBtn.disabled = true;
    runBtn.innerHTML = '<span>⏳ Testing…</span>';
    set('eval-console-output', `Executing code in secure ${lang.toUpperCase()} environment…`);

    try {
      const res = await practiceApi.testRun(currentProblem.id, code, lang);
      displayEvaluationResults(res, false);
    } catch (err) {
      set('eval-console-output', `⚠️ Test execution error: ${err.message}`);
    } finally {
      runBtn.disabled = false;
      runBtn.innerHTML = '▶ Run Sample Tests';
    }
  });

  // Submit Solution
  submitBtn?.addEventListener('click', async () => {
    if (!currentProblem || !editor) return;
    const code = editor.getValue();
    const lang = langSelect ? langSelect.value : 'python';

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>⚡ Evaluating…</span>';
    set('eval-console-output', `Submitting ${lang.toUpperCase()} solution and recording performance…`);

    try {
      const res = await practiceApi.submit(currentProblem.id, code, lang);
      displayEvaluationResults(res, true);

      // Update local checkmark state
      attemptedProblemIds.add(currentProblem.id);
      if (res.score >= 70) {
        solvedProblemIds.add(currentProblem.id);
        showToast(`🎉 Challenge Solved! Score: ${res.score}%`, 'success');
      } else {
        showToast(`Score: ${res.score}%. Keep refining your logic!`, 'warning');
      }

      // Re-render lists to update checkmarks immediately
      renderCatalogTable(currentProblems);
      renderSidebarList(currentProblems);

      // Update counters
      const solvedCount = currentProblems.filter(p => solvedProblemIds.has(p.id)).length;
      set('topic-solved-counter', `${solvedCount} Solved`);
    } catch (err) {
      set('eval-console-output', `⚠️ Submission error: ${err.message}`);
      showToast(err.message, 'error');
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '⚡ Submit Solution';
    }
  });

  // Reset Starter Code
  resetBtn?.addEventListener('click', () => {
    if (!currentProblem || !editor) return;
    const lang = langSelect ? langSelect.value : 'python';
    const cfg = LANG_TEMPLATES[lang] || LANG_TEMPLATES.python;
    localStorage.removeItem(`pym_practice_draft_${currentProblem.id}_${lang}`);
    if (lang === 'python') localStorage.removeItem(`pym_practice_draft_${currentProblem.id}`);
    editor.setValue(cfg.template(currentProblem));
    showToast(`Starter code for ${lang.toUpperCase()} restored`, 'info');
  });

  // Reveal Hints
  revealHintBtn?.addEventListener('click', () => {
    if (!currentProblem || !currentProblem.hints) return;
    const hints = currentProblem.hints;
    if (revealedHintsCount < hints.length) {
      revealedHintsCount++;
      const container = document.getElementById('ws-hints-container');
      if (container) {
        container.innerHTML = hints.slice(0, revealedHintsCount).map((h, i) => `
          <div style="background:#FFFDF9;border-left:3px solid #F59E0B;padding:10px 14px;border-radius:6px;margin-bottom:8px;font-size:13px;color:#1C0E04;">
            <strong>Hint ${i + 1}:</strong> ${escapeHtml(h)}
          </div>
        `).join('');
      }
      set('ws-hint-count', `${revealedHintsCount}/${hints.length}`);
    } else {
      showToast('All hints have been revealed!', 'info');
    }
  });

  // Right pane tab switching
  const tabs = [
    { btn: 'tab-ws-problem', pane: 'ws-pane-problem' },
    { btn: 'tab-ws-tests', pane: 'ws-pane-tests' },
    { btn: 'tab-ws-subs', pane: 'ws-pane-subs' },
    { btn: 'tab-ws-hints', pane: 'ws-pane-hints' },
  ];

  tabs.forEach(t => {
    const btn = document.getElementById(t.btn);
    btn?.addEventListener('click', () => {
      tabs.forEach(x => {
        document.getElementById(x.btn)?.classList.remove('active');
        document.getElementById(x.pane)?.classList.add('hidden');
      });
      btn.classList.add('active');
      document.getElementById(t.pane)?.classList.remove('hidden');
    });
  });

  // Back to catalog button
  document.getElementById('btn-back-to-catalog')?.addEventListener('click', () => {
    switchToCatalogView();
  });
}

/* ── 8. Display Test Evaluation Results in Output Console ─────────────────── */
function displayEvaluationResults(res, isSubmission) {
  const consoleBox = document.getElementById('eval-console-output');
  if (!consoleBox) return;

  const passed = res.passed || 0;
  const total = res.total || 0;
  const score = res.score ?? Math.round((passed / total) * 100);
  const isAllPassed = passed === total && total > 0;

  const statusColor = isAllPassed ? '#10B981' : score >= 70 ? '#F59E0B' : '#EF4444';
  const headerText = isAllPassed
    ? `🎉 ALL TESTS PASSED! (${passed}/${total}) — Score: ${score}%`
    : `⚠️ TESTS COMPLETED: ${passed}/${total} Passed — Score: ${score}%`;

  let detailsHtml = '';
  if (Array.isArray(res.results)) {
    detailsHtml = res.results.map((r, i) => {
      const passColor = r.passed ? '#10B981' : '#EF4444';
      const icon = r.passed ? '✓' : '✗';
      return `
        <div style="margin-top:6px;padding:6px 10px;background:rgba(255,255,255,0.04);border-radius:6px;border-left:3px solid ${passColor};">
          <span style="color:${passColor};font-weight:700;">${icon} Case ${i + 1}: ${escapeHtml(r.description || 'Test')}</span>
          ${!r.passed ? `<br><span style="color:#94A3B8;">Expected: <code>${escapeHtml(r.expected || '')}</code> | Got: <code>${escapeHtml(r.actual || r.error || '')}</code></span>` : ''}
        </div>
      `;
    }).join('');
  }

  consoleBox.innerHTML = `
    <div style="font-size:13.5px;font-weight:800;color:${statusColor};">${headerText}</div>
    ${res.feedback ? `<div style="color:#E2E8F0;margin-top:6px;font-size:12.5px;">${escapeHtml(res.feedback)}</div>` : ''}
    ${detailsHtml}
  `;
}

/* ── 9. Setup Catalog Filters & Search ─────────────────────────────────────── */
function setupCatalogFilters() {
  const searchInput = document.getElementById('catalog-search-input');
  const diffSelect = document.getElementById('catalog-diff-filter');
  const statusSelect = document.getElementById('catalog-status-filter');
  const sidebarSearch = document.getElementById('sidebar-prob-search');

  const filterCatalog = () => {
    catalogCurrentPage = 1;
    const q = (searchInput?.value || '').toLowerCase().trim();
    const diff = diffSelect?.value || 'all';
    const st = statusSelect?.value || 'all';

    const filtered = currentProblems.filter(p => {
      const matchQ = !q || p.title.toLowerCase().includes(q) || (p.description || '').toLowerCase().includes(q);
      const matchDiff = diff === 'all' || p.difficulty.toLowerCase() === diff;
      
      const isSolved = solvedProblemIds.has(p.id);
      const isAttempted = attemptedProblemIds.has(p.id);
      const matchStatus = st === 'all'
        || (st === 'solved' && isSolved)
        || (st === 'attempted' && isAttempted && !isSolved)
        || (st === 'unsolved' && !isAttempted);

      return matchQ && matchDiff && matchStatus;
    });

    renderCatalogTable(filtered);
  };

  searchInput?.addEventListener('input', filterCatalog);
  diffSelect?.addEventListener('change', filterCatalog);
  statusSelect?.addEventListener('change', filterCatalog);

  // Pagination navigation button listeners
  document.getElementById('btn-page-prev')?.addEventListener('click', () => {
    if (catalogCurrentPage > 1) {
      catalogCurrentPage--;
      renderCatalogTable();
    }
  });

  document.getElementById('btn-page-next')?.addEventListener('click', () => {
    const totalPages = Math.ceil(currentFilteredProblems.length / CATALOG_PAGE_SIZE);
    if (catalogCurrentPage < totalPages) {
      catalogCurrentPage++;
      renderCatalogTable();
    }
  });

  // Sidebar filter (if present)
  sidebarSearch?.addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase().trim();
    const filtered = currentProblems.filter(p => !q || p.title.toLowerCase().includes(q));
    renderSidebarList(filtered);
  });
}

/* ── 10. View Mode Toggling ────────────────────────────────────────────────── */
function setupViewToggles() {
  const btnCatalog = document.getElementById('toggle-catalog-view');
  const btnWorkspace = document.getElementById('toggle-workspace-view');

  btnCatalog?.addEventListener('click', switchToCatalogView);
  btnWorkspace?.addEventListener('click', switchToWorkspaceView);
}

function switchToCatalogView() {
  document.getElementById('toggle-catalog-view')?.classList.add('active');
  document.getElementById('toggle-workspace-view')?.classList.remove('active');
  document.getElementById('catalog-view-section')?.classList.remove('hidden');
  document.getElementById('workspace-view-section')?.classList.add('hidden');
}

function switchToWorkspaceView() {
  document.getElementById('toggle-catalog-view')?.classList.remove('active');
  document.getElementById('toggle-workspace-view')?.classList.add('active');
  document.getElementById('catalog-view-section')?.classList.add('hidden');
  document.getElementById('workspace-view-section')?.classList.remove('hidden');

  if (editor && editor.refresh) {
    setTimeout(() => editor.refresh(), 100);
  }
}

/* ── 11. Practice Timer ───────────────────────────────────────────────────── */
function startTimer() {
  if (timerInterval) clearInterval(timerInterval);
  timerSeconds = 0;
  timerInterval = setInterval(() => {
    timerSeconds++;
    const mins = Math.floor(timerSeconds / 60);
    set('workspace-timer', `${mins}m spent`);
  }, 1000);
}

function set(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

init();
