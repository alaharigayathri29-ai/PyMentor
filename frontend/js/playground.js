/**
 * playground.js
 * Multi-Language Playground Controller (Real Multi-Page Application)
 * Supports Python (backend execution sandbox with stdin/stdout)
 * and Full Web Application (HTML5, CSS3, JavaScript with live interactive preview and browser console).
 */

import { requireAuth, initLayout, escapeHtml } from './common.js?v=20261108_v17';
import { workspaceApi } from './api.js?v=20261108_v17';
import { createCodeEditor } from './components/editor.js?v=20261108_v17';
import { showToast } from './components/toast.js?v=20261108_v17';
import { showPromptModal, showConfirmModal } from './components/modal.js?v=20261108_v17';

let editor = null;
let savedPrograms = [];
let currentLoadedProjectId = null;
let currentLoadedProjectTitle = null;

// Current IDE State
let currentLang = 'python'; // 'python' | 'web'
let activeWebFile = 'html';  // 'html' | 'css' | 'js'
let activeWebSubtab = 'preview'; // 'preview' | 'console'

let pythonCode = `# Write your Python code here\nprint("Hello from Python Playground!")\n`;

const WEB_TEMPLATES = {
  counter: {
    html: `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Interactive Counter</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="card">
    <div class="badge">🌐 Interactive Web App</div>
    <h1>Interactive Counter</h1>
    <p>Edit HTML, CSS, and JS to build frontend apps live in your browser.</p>
    <div class="counter-box">
      <button id="btn-decrement">-</button>
      <span id="counter-val">0</span>
      <button id="btn-increment">+</button>
    </div>
  </div>
  <script src="script.js"></script>
</body>
</html>`,
    css: `* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #F1F5F9;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 20px;
}
.card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 28px;
  max-width: 420px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}
.badge {
  display: inline-block;
  background: #EFF6FF;
  color: #2563EB;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 100px;
  margin-bottom: 14px;
}
h1 { color: #0F172A; font-size: 22px; margin-bottom: 8px; }
p { color: #64748B; font-size: 14px; line-height: 1.5; margin-bottom: 20px; }
.counter-box {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  background: #F8FAFC;
  padding: 12px;
  border-radius: 8px;
}
button {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  border: none;
  background: #2563EB;
  color: white;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.15s;
}
button:hover { background: #1D4ED8; }
#counter-val { font-size: 24px; font-weight: 800; color: #0F172A; min-width: 40px; }`,
    js: `let count = 0;
const valEl = document.getElementById('counter-val');
const incBtn = document.getElementById('btn-increment');
const decBtn = document.getElementById('btn-decrement');

incBtn.addEventListener('click', () => {
  count++;
  valEl.textContent = count;
  console.log('Counter value is now:', count);
});

decBtn.addEventListener('click', () => {
  count--;
  valEl.textContent = count;
  console.log('Counter value is now:', count);
});

console.log('Interactive Counter application loaded successfully!');`
  },
  todo: {
    html: `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Todo App</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="todo-app">
    <h2>📝 Task Manager</h2>
    <div class="input-row">
      <input type="text" id="task-input" placeholder="Enter a new task...">
      <button id="add-btn">Add</button>
    </div>
    <ul id="task-list"></ul>
  </div>
  <script src="script.js"></script>
</body>
</html>`,
    css: `* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #F8FAFC;
  display: flex;
  justify-content: center;
  padding: 30px 15px;
}
.todo-app {
  background: white;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
  padding: 24px;
  width: 100%;
  max-width: 440px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
}
h2 { color: #1E293B; margin-bottom: 16px; font-size: 20px; }
.input-row { display: flex; gap: 8px; margin-bottom: 16px; }
input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #CBD5E1;
  border-radius: 6px;
  outline: none;
}
input:focus { border-color: #2563EB; }
button {
  background: #2563EB;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}
ul { list-style: none; }
li {
  padding: 8px 12px;
  border-bottom: 1px solid #F1F5F9;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #334155;
  font-size: 14px;
}
li:last-child { border-bottom: none; }
.del-btn {
  background: #FEE2E2;
  color: #DC2626;
  border: none;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
}`,
    js: `const input = document.getElementById('task-input');
const addBtn = document.getElementById('add-btn');
const list = document.getElementById('task-list');

function addTask() {
  const text = input.value.trim();
  if (!text) return;
  const li = document.createElement('li');
  li.innerHTML = '<span>' + text + '</span><button class="del-btn">✕</button>';
  li.querySelector('.del-btn').addEventListener('click', () => {
    li.remove();
    console.log('Task deleted:', text);
  });
  list.appendChild(li);
  console.log('Task added:', text);
  input.value = '';
}

addBtn.addEventListener('click', addTask);
input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') addTask();
});

console.log('Todo application ready!');`
  },
  card: {
    html: `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Student Profile</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="profile-card">
    <div class="avatar">👨‍💻</div>
    <h3>Full-Stack Developer</h3>
    <p>Building responsive web apps & mastering Python algorithms.</p>
    <div class="skills">
      <span>HTML5</span>
      <span>CSS3</span>
      <span>JavaScript</span>
      <span>Python</span>
    </div>
    <button id="like-btn">❤️ Like (<span id="likes">0</span>)</button>
  </div>
  <script src="script.js"></script>
</body>
</html>`,
    css: `* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #EEF2F6;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
}
.profile-card {
  background: white;
  border-radius: 16px;
  padding: 32px 24px;
  text-align: center;
  max-width: 320px;
  box-shadow: 0 10px 25px -5px rgba(0,0,0,0.08);
}
.avatar { font-size: 48px; margin-bottom: 12px; }
h3 { color: #1E293B; font-size: 18px; margin-bottom: 6px; }
p { color: #64748B; font-size: 13px; line-height: 1.5; margin-bottom: 18px; }
.skills { display: flex; flex-wrap: wrap; gap: 6px; justify-content: center; margin-bottom: 20px; }
.skills span {
  background: #F1F5F9;
  color: #475569;
  font-size: 11px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 6px;
}
button {
  width: 100%;
  padding: 10px;
  background: #2563EB;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}
button:hover { background: #1D4ED8; }`,
    js: `let likes = 0;
const likeBtn = document.getElementById('like-btn');
const likesSpan = document.getElementById('likes');

likeBtn.addEventListener('click', () => {
  likes++;
  likesSpan.textContent = likes;
  console.log('Profile liked! Total:', likes);
});

console.log('Profile card ready!');`
  },
  blank: {
    html: `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Blank App</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <h1>Hello Web!</h1>
  <script src="script.js"></script>
</body>
</html>`,
    css: `body {
  font-family: sans-serif;
  padding: 20px;
  background: #FFFFFF;
  color: #1E293B;
}`,
    js: `console.log('Blank project initialized.');`
  }
};

let webFiles = {
  html: WEB_TEMPLATES.counter.html,
  css: WEB_TEMPLATES.counter.css,
  js: WEB_TEMPLATES.counter.js,
};

let browserLogs = [];

async function init() {
  const user = await requireAuth();
  if (!user) return;

  initLayout('playground', user);

  const mountEl = document.getElementById('pg-editor-mount');
  const runBtn = document.getElementById('pg-btn-run');
  const resetBtn = document.getElementById('pg-btn-reset');
  const clearBtn = document.getElementById('pg-btn-clear');
  const saveBtn = document.getElementById('pg-btn-save');
  const libraryBtn = document.getElementById('pg-btn-saved-list');
  const modalClose = document.getElementById('pg-modal-close');
  const libraryModal = document.getElementById('pg-library-modal');
  const templateSelect = document.getElementById('pg-template-select');
  const popoutBtn = document.getElementById('btn-popout-preview');

  // Check if a code snippet was transferred from a lesson
  const passedCode = sessionStorage.getItem('playground_code');
  if (passedCode) {
    pythonCode = passedCode;
    sessionStorage.removeItem('playground_code');
  }

  // Create CodeMirror instance
  if (mountEl) {
    editor = createCodeEditor(mountEl, pythonCode, false, 'python');
  }

  // Bind Language Selector Tabs
  document.querySelectorAll('#pg-lang-tabs .lang-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const lang = btn.dataset.lang;
      switchLanguage(lang);
    });
  });

  // Bind Web App File Tabs
  document.querySelectorAll('#pg-web-file-tabs .file-tab').forEach(btn => {
    btn.addEventListener('click', () => {
      const file = btn.dataset.file;
      switchWebFile(file);
    });
  });

  // Bind Web App Output Subtabs (Live Preview vs Browser Console)
  document.getElementById('btn-subtab-preview')?.addEventListener('click', () => switchWebSubtab('preview'));
  document.getElementById('btn-subtab-console')?.addEventListener('click', () => switchWebSubtab('console'));

  // Template select change
  templateSelect?.addEventListener('change', (e) => {
    const key = e.target.value;
    if (WEB_TEMPLATES[key]) {
      webFiles = {
        html: WEB_TEMPLATES[key].html,
        css: WEB_TEMPLATES[key].css,
        js: WEB_TEMPLATES[key].js,
      };
      if (editor) {
        editor.setValue(webFiles[activeWebFile]);
      }
      runPlaygroundCode();
      showToast(`Loaded ${key} template.`, 'info');
    }
  });

  // Run Code
  runBtn?.addEventListener('click', runPlaygroundCode);

  // Popout preview to new browser window
  popoutBtn?.addEventListener('click', () => {
    saveCurrentEditorCode();
    const compiled = compileWebProject();
    const win = window.open('', '_blank');
    if (win) {
      win.document.open();
      win.document.write(compiled);
      win.document.close();
    }
  });

  // Keyboard shortcut Ctrl+Enter / Cmd+Enter to run
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      runPlaygroundCode();
    }
  });

  // Reset editor
  resetBtn?.addEventListener('click', () => {
    if (currentLang === 'python') {
      pythonCode = `# Write your Python code here\nprint("Hello from Python Playground!")\n`;
      if (editor) editor.setValue(pythonCode);
      showToast('Python editor reset.', 'info');
    } else {
      const def = WEB_TEMPLATES.counter;
      webFiles = { html: def.html, css: def.css, js: def.js };
      if (editor) editor.setValue(webFiles[activeWebFile]);
      runPlaygroundCode();
      showToast('Web project reset to starter template.', 'info');
    }
  });

  // Clear output terminal or browser console
  clearBtn?.addEventListener('click', () => {
    if (currentLang === 'python') {
      const consoleOutput = document.getElementById('pg-console-output');
      const statusBadge = document.getElementById('pg-status-badge');
      const execTime = document.getElementById('pg-exec-time');
      if (consoleOutput) consoleOutput.textContent = 'Ready. Write Python code and click "Run Code".';
      if (statusBadge) {
        statusBadge.textContent = 'Idle';
        statusBadge.className = 'badge badge-gray';
      }
      if (execTime) execTime.textContent = '0 ms';
    } else {
      browserLogs = [];
      renderBrowserLogs();
      showToast('Browser console cleared.', 'info');
    }
  });

  // Save script/project to real backend database
  saveBtn?.addEventListener('click', saveCurrentScript);

  // Library modal
  libraryBtn?.addEventListener('click', () => {
    loadSavedLibrary();
    if (libraryModal) {
      libraryModal.classList.remove('hidden');
    }
  });

  const closeLibModal = () => {
    if (libraryModal) {
      libraryModal.classList.add('hidden');
    }
  };

  modalClose?.addEventListener('click', closeLibModal);

  libraryModal?.addEventListener('click', (e) => {
    if (e.target === libraryModal) closeLibModal();
  });

  // Listen for iframe console messages via postMessage
  window.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'CONSOLE_LOG') {
      const logEntry = {
        level: event.data.level || 'log',
        msg: event.data.msg || '',
        time: new Date().toLocaleTimeString(),
      };
      browserLogs.push(logEntry);
      renderBrowserLogs();
    }
  });

  // Update library count from real database
  await updateLibraryCount();

  // Handle "New Project" button to start a fresh workspace
  const newProjBtn = document.getElementById('pg-btn-new-project');
  newProjBtn?.addEventListener('click', () => {
    currentLoadedProjectId = null;
    currentLoadedProjectTitle = null;
    const badge = document.getElementById('pg-active-project-badge');
    if (badge) {
      badge.textContent = '';
      badge.classList.add('hidden');
    }
    const topbarTitle = document.getElementById('topbar-title');
    if (currentLang === 'python') {
      if (topbarTitle) topbarTitle.textContent = 'Python Code Playground';
      pythonCode = `# Write your Python code here\nprint("Hello from Python Playground!")\n`;
      if (editor) editor.setValue(pythonCode);
    } else {
      if (topbarTitle) topbarTitle.textContent = 'Web Application Playground (HTML / CSS / JS)';
      const def = WEB_TEMPLATES.counter;
      webFiles = { html: def.html, css: def.css, js: def.js };
      activeWebFile = 'html';
      if (editor) editor.setValue(webFiles.html);
      runPlaygroundCode();
    }
    showToast('Started new workspace project.', 'info');
  });

  // Check URL parameters for explicit project to open: ?project=X or ?id=X
  const urlParams = new URLSearchParams(window.location.search);
  const targetId = parseInt(urlParams.get('project') || urlParams.get('id') || '', 10);

  if (targetId) {
    const found = savedPrograms.find(p => p.id === targetId);
    if (found) {
      loadProjectIntoWorkspace(found);
    } else {
      try {
        const fetched = await workspaceApi.getProgram(targetId);
        loadProjectIntoWorkspace(fetched);
      } catch (err) {
        console.warn('Could not load project from URL param:', err);
      }
    }
  } else if (savedPrograms && savedPrograms.length > 0) {
    // Automatically open the student's saved workspace project!
    loadProjectIntoWorkspace(savedPrograms[0]);
  }
}

function saveCurrentEditorCode() {
  if (!editor) return;
  const currentVal = editor.getValue();
  if (currentLang === 'python') {
    pythonCode = currentVal;
  } else {
    webFiles[activeWebFile] = currentVal;
  }
}

function switchLanguage(lang) {
  if (lang === currentLang) return;
  saveCurrentEditorCode();
  currentLang = lang;

  // Update tabs visual
  document.querySelectorAll('#pg-lang-tabs .lang-tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.lang === lang);
  });

  const webFileTabs = document.getElementById('pg-web-file-tabs');
  const templateSelect = document.getElementById('pg-template-select');
  const stdinDrawer = document.getElementById('pg-stdin-drawer');
  const pythonHeader = document.getElementById('pg-python-console-header');
  const webHeader = document.getElementById('pg-web-console-header');
  const pythonOutput = document.getElementById('pg-console-output');
  const webPreview = document.getElementById('pg-web-preview-container');
  const browserConsole = document.getElementById('pg-browser-console-list');
  const topbarTitle = document.getElementById('topbar-title');
  const statusBadge = document.getElementById('pg-status-badge');

  if (lang === 'python') {
    topbarTitle.textContent = 'Python Code Playground';
    webFileTabs?.classList.add('hidden');
    templateSelect?.classList.add('hidden');
    stdinDrawer?.classList.remove('hidden');
    pythonHeader?.classList.remove('hidden');
    webHeader?.classList.add('hidden');
    pythonOutput?.classList.remove('hidden');
    webPreview?.classList.add('hidden');
    browserConsole?.classList.add('hidden');

    if (editor) {
      editor.setOption('mode', 'python');
      editor.setValue(pythonCode);
    }
  } else {
    topbarTitle.textContent = 'Web Application Playground (HTML / CSS / JS)';
    webFileTabs?.classList.remove('hidden');
    templateSelect?.classList.remove('hidden');
    stdinDrawer?.classList.add('hidden');
    pythonHeader?.classList.add('hidden');
    webHeader?.classList.remove('hidden');
    pythonOutput?.classList.add('hidden');

    switchWebSubtab(activeWebSubtab);
    switchWebFile(activeWebFile, false);

    // Initial compile and run web project
    runPlaygroundCode();
  }

  if (statusBadge) {
    statusBadge.textContent = 'Idle';
    statusBadge.className = 'badge badge-gray';
  }
}

function switchWebFile(file, savePrevious = true) {
  if (savePrevious) saveCurrentEditorCode();
  activeWebFile = file;

  document.querySelectorAll('#pg-web-file-tabs .file-tab').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.file === file);
  });

  const modeMap = {
    html: 'htmlmixed',
    css: 'css',
    js: 'javascript',
  };

  if (editor) {
    editor.setOption('mode', modeMap[file] || 'htmlmixed');
    editor.setValue(webFiles[file] || '');
  }
}

function switchWebSubtab(tab) {
  activeWebSubtab = tab;
  const btnPrev = document.getElementById('btn-subtab-preview');
  const btnCons = document.getElementById('btn-subtab-console');
  const webPreview = document.getElementById('pg-web-preview-container');
  const browserConsole = document.getElementById('pg-browser-console-list');

  btnPrev?.classList.toggle('active', tab === 'preview');
  btnCons?.classList.toggle('active', tab === 'console');

  if (tab === 'preview') {
    webPreview?.classList.remove('hidden');
    browserConsole?.classList.add('hidden');
  } else {
    webPreview?.classList.add('hidden');
    browserConsole?.classList.remove('hidden');
  }
}

function compileWebProject() {
  saveCurrentEditorCode();
  const html = webFiles.html || '';
  const css = webFiles.css || '';
  const js = webFiles.js || '';

  const interceptorScript = `
    <script>
      (function() {
        function _post(level, args) {
          try {
            var msg = Array.from(args).map(function(item) {
              if (typeof item === 'object') {
                try { return JSON.stringify(item); } catch(e) { return String(item); }
              }
              return String(item);
            }).join(' ');
            window.parent.postMessage({ type: 'CONSOLE_LOG', level: level, msg: msg }, '*');
          } catch(e) {}
        }
        var _log = console.log, _info = console.info, _warn = console.warn, _error = console.error;
        console.log = function() { _post('log', arguments); _log.apply(console, arguments); };
        console.info = function() { _post('info', arguments); _info.apply(console, arguments); };
        console.warn = function() { _post('warn', arguments); _warn.apply(console, arguments); };
        console.error = function() { _post('error', arguments); _error.apply(console, arguments); };
        window.onerror = function(msg, url, line) {
          _post('error', ['[Uncaught Error]: ' + msg + ' (Line ' + line + ')']);
        };
      })();
    <\/script>
  `;

  // Inject style and scripts into HTML
  let compiled = html;
  if (!compiled.includes('<head>')) {
    compiled = '<!DOCTYPE html><html><head></head><body>' + compiled + '</body></html>';
  }

  // Inject CSS
  compiled = compiled.replace('</head>', `<style>\n${css}\n</style>\n${interceptorScript}\n</head>`);

  // Inject JS before closing body
  if (compiled.includes('</body>')) {
    compiled = compiled.replace('</body>', `<script>\n${js}\n<\/script>\n</body>`);
  } else {
    compiled += `<script>\n${js}\n<\/script>`;
  }

  return compiled;
}

function renderBrowserLogs() {
  const container = document.getElementById('pg-browser-console-list');
  const countBadge = document.getElementById('pg-console-count');
  if (countBadge) countBadge.textContent = browserLogs.length;
  if (!container) return;

  if (browserLogs.length === 0) {
    container.innerHTML = '<div style="padding:16px;text-align:center;color:var(--text-muted);font-size:12px;">No console logs yet. Interactive output from console.log() will appear here.</div>';
    return;
  }

  container.innerHTML = browserLogs.map(l => `
    <div class="console-log-row ${l.level}">
      <span style="color:var(--text-muted);font-size:10.5px;">[${l.time}]</span>
      <span style="font-weight:700;text-transform:uppercase;font-size:10.5px;min-width:44px;">${l.level}</span>
      <span>${escapeHtml(l.msg)}</span>
    </div>
  `).join('');

  container.scrollTop = container.scrollHeight;
}

async function runPlaygroundCode() {
  if (!editor) return;

  const runBtn = document.getElementById('pg-btn-run');
  const statusBadge = document.getElementById('pg-status-badge');

  if (currentLang === 'web') {
    // Web application execution (Client-side interactive iframe)
    browserLogs = [];
    renderBrowserLogs();

    const iframe = document.getElementById('pg-web-preview-iframe');
    const compiled = compileWebProject();

    if (iframe) {
      iframe.srcdoc = compiled;
    }

    if (statusBadge) {
      statusBadge.textContent = 'Active (Live)';
      statusBadge.className = 'badge badge-green';
    }

    showToast('Live preview updated.', 'success');
    return;
  }

  // Python Sandbox Execution (Backend code runner)
  saveCurrentEditorCode();
  const code = pythonCode;
  if (!code.trim()) {
    showToast('Cannot run empty code.', 'warn');
    return;
  }

  const stdinInput = document.getElementById('pg-stdin-input')?.value || '';
  const consoleOutput = document.getElementById('pg-console-output');
  const execTime = document.getElementById('pg-exec-time');

  if (runBtn) {
    runBtn.disabled = true;
    runBtn.innerHTML = '<span>⏳ Running…</span>';
  }

  if (statusBadge) {
    statusBadge.textContent = 'Running';
    statusBadge.className = 'badge badge-blue';
  }

  if (consoleOutput) {
    consoleOutput.textContent = 'Executing sandbox environment…\n';
  }

  try {
    const startTime = performance.now();
    const result = await workspaceApi.runCode(code, stdinInput);
    const duration = Math.round(performance.now() - startTime);

    if (execTime) execTime.textContent = `${duration} ms`;

    if (result.success) {
      if (statusBadge) {
        statusBadge.textContent = 'Success';
        statusBadge.className = 'badge badge-green';
      }
      if (consoleOutput) {
        const out = result.stdout !== undefined ? result.stdout : (result.output || '');
        consoleOutput.textContent = out.trim() ? out : '(Execution finished with no output)';
      }
    } else {
      if (statusBadge) {
        statusBadge.textContent = result.error_type || 'Error';
        statusBadge.className = 'badge badge-red';
      }
      if (consoleOutput) {
        consoleOutput.textContent = (result.stderr || result.error || 'Execution encountered an error.').trim();
      }
    }
  } catch (err) {
    if (statusBadge) {
      statusBadge.textContent = 'Failed';
      statusBadge.className = 'badge badge-red';
    }
    if (consoleOutput) {
      consoleOutput.textContent = `Execution failed: ${err.message}`;
    }
    showToast(`Execution failed: ${err.message}`, 'error');
  } finally {
    if (runBtn) {
      runBtn.disabled = false;
      runBtn.innerHTML = '<span>▶ Run Code</span>';
    }
  }
}

async function saveCurrentScript() {
  saveCurrentEditorCode();

  // If already working on a loaded project, offer to update or save new
  if (currentLoadedProjectId) {
    const updateChoice = await showConfirmModal({
      title: `Update "${currentLoadedProjectTitle}"?`,
      message: `Do you want to save changes to "${currentLoadedProjectTitle}", or save as a new copy?`,
      confirmText: 'Update Project',
      cancelText: 'Save as New Copy',
      isDanger: false,
    });

    if (updateChoice) {
      try {
        const payload = {
          title: currentLoadedProjectTitle,
          language: currentLang,
          code: currentLang === 'python' ? pythonCode : webFiles.html,
          extra_data: currentLang === 'web' ? { css: webFiles.css, js: webFiles.js } : null,
        };
        await workspaceApi.updateProgram(currentLoadedProjectId, payload);
        showToast(`Saved changes to project "${currentLoadedProjectTitle}"!`, 'success');
        updateLibraryCount();
        return;
      } catch (err) {
        showToast(`Update failed: ${err.message}`, 'error');
        return;
      }
    }
  }

  if (currentLang === 'python') {
    if (!pythonCode.trim()) {
      showToast('Cannot save empty Python script.', 'warn');
      return;
    }
    const title = await showPromptModal({
      title: 'Save Python Script',
      message: 'Enter a name for this Python script:',
      placeholder: 'e.g. My Algorithm, Data Parser',
      defaultValue: currentLoadedProjectTitle ? `${currentLoadedProjectTitle} (Copy)` : 'Python Script',
      confirmText: 'Save Script',
    });
    if (!title || !title.trim()) return;

    try {
      const created = await workspaceApi.createProgram({
        title: title.trim(),
        language: 'python',
        code: pythonCode,
      });
      currentLoadedProjectId = created.id;
      currentLoadedProjectTitle = created.title;
      showToast(`Saved Python script "${title.trim()}"!`, 'success');
      updateLibraryCount();
    } catch (err) {
      showToast(`Failed to save program: ${err.message}`, 'error');
    }
  } else {
    const title = await showPromptModal({
      title: 'Save Web Project',
      message: 'Enter a name for this Web Application project:',
      placeholder: 'e.g. Interactive Calculator, Portfolio App',
      defaultValue: currentLoadedProjectTitle ? `${currentLoadedProjectTitle} (Copy)` : 'Web Project',
      confirmText: 'Save Project',
    });
    if (!title || !title.trim()) return;

    try {
      const created = await workspaceApi.createProgram({
        title: title.trim(),
        language: 'web',
        code: webFiles.html,
        extra_data: {
          css: webFiles.css,
          js: webFiles.js,
        },
      });
      currentLoadedProjectId = created.id;
      currentLoadedProjectTitle = created.title;
      showToast(`Saved Web Project "${title.trim()}"!`, 'success');
      updateLibraryCount();
    } catch (err) {
      showToast(`Failed to save project: ${err.message}`, 'error');
    }
  }
}

async function updateLibraryCount() {
  const badge = document.getElementById('pg-saved-count');
  try {
    savedPrograms = await workspaceApi.listPrograms();
    if (badge) badge.textContent = savedPrograms.length;
  } catch {
    if (badge) badge.textContent = '0';
  }
}

async function loadSavedLibrary() {
  const container = document.getElementById('pg-saved-list-items');
  if (!container) return;

  container.innerHTML = '<div style="text-align:center;padding:24px;"><div class="spinner"></div></div>';

  try {
    savedPrograms = await workspaceApi.listPrograms();

    if (!savedPrograms || savedPrograms.length === 0) {
      container.innerHTML = `
        <div style="text-align:center;padding:32px 16px;color:var(--text-secondary);">
          <div style="font-size:32px;margin-bottom:8px;">📁</div>
          <p style="font-weight:600;color:var(--text-primary);margin-bottom:4px;">No saved projects yet</p>
          <p style="font-size:12.5px;color:var(--text-muted);">Write code in the editor and click "Save Project" to store it in your account.</p>
        </div>
      `;
      return;
    }

    container.innerHTML = savedPrograms.map(p => {
      const isWeb = p.language === 'web';
      return `
        <div style="display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:#F8FAFC;border:1px solid var(--border);border-radius:var(--r-md);margin-bottom:10px;">
          <div>
            <div style="display:flex;align-items:center;gap:8px;">
              <span class="badge ${isWeb ? 'badge-blue' : 'badge-green'}" style="font-size:10.5px;padding:2px 6px;">
                ${isWeb ? '🌐 Web App' : '🐍 Python'}
              </span>
              <span style="font-weight:600;font-size:13.5px;color:var(--text-primary);">${escapeHtml(p.title)}</span>
            </div>
            <div style="font-size:11.5px;color:var(--text-muted);margin-top:4px;">
              Saved ${new Date(p.created_at).toLocaleDateString()}
            </div>
          </div>
          <div style="display:flex;gap:6px;">
            <button class="btn btn-primary btn-sm btn-load-prog" data-id="${p.id}">Load</button>
            <button class="btn btn-ghost btn-sm btn-del-prog" data-id="${p.id}" style="color:var(--danger);padding:4px 8px;">✕</button>
          </div>
        </div>
      `;
    }).join('');

    // Load project listener
    container.querySelectorAll('.btn-load-prog').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = parseInt(btn.getAttribute('data-id'), 10);
        const prog = savedPrograms.find(p => p.id === id);
        if (!prog) return;
        await loadProjectIntoWorkspace(prog);
      });
    });

    // Delete project listener
    container.querySelectorAll('.btn-del-prog').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = parseInt(btn.getAttribute('data-id'), 10);
        const ok = await showConfirmModal({
          title: 'Delete Saved Project',
          message: 'Are you sure you want to delete this saved project? This action cannot be undone.',
          confirmText: 'Delete',
          cancelText: 'Cancel',
          isDanger: true,
        });
        if (!ok) return;
        try {
          await workspaceApi.deleteProgram(id);
          showToast('Project deleted.', 'info');
          updateLibraryCount();
          loadSavedLibrary();
        } catch (err) {
          showToast(`Delete failed: ${err.message}`, 'error');
        }
      });
    });

  } catch (err) {
    container.innerHTML = `<div class="alert alert-error">Failed to load saved projects: ${err.message}</div>`;
  }
}

export async function loadProjectIntoWorkspace(prog) {
  if (!prog) return;

  currentLoadedProjectId = prog.id;
  currentLoadedProjectTitle = prog.title;

  // Update visual active project badge in toolbar
  const badge = document.getElementById('pg-active-project-badge');
  if (badge) {
    badge.textContent = `📁 ${prog.title}`;
    badge.title = `Currently editing: ${prog.title} (ID #${prog.id})`;
    badge.classList.remove('hidden');
  }

  // Parse extra_data safely whether JSON string or object
  let extra = prog.extra_data;
  if (typeof extra === 'string') {
    try { extra = JSON.parse(extra); } catch { extra = {}; }
  }
  if (!extra || typeof extra !== 'object') extra = {};

  const isWeb = prog.language === 'web';

  if (isWeb) {
    currentLang = 'web';
    webFiles = {
      html: prog.code || '',
      css: extra.css || '',
      js: extra.js || '',
    };
    activeWebFile = 'html';

    // Update Language Tabs UI
    document.querySelectorAll('#pg-lang-tabs .lang-tab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.lang === 'web');
    });

    const webFileTabs = document.getElementById('pg-web-file-tabs');
    const templateSelect = document.getElementById('pg-template-select');
    const stdinDrawer = document.getElementById('pg-stdin-drawer');
    const pythonHeader = document.getElementById('pg-python-console-header');
    const webHeader = document.getElementById('pg-web-console-header');
    const pythonOutput = document.getElementById('pg-console-output');
    const topbarTitle = document.getElementById('topbar-title');

    if (topbarTitle) topbarTitle.textContent = `Web Application Playground — ${prog.title}`;
    webFileTabs?.classList.remove('hidden');
    templateSelect?.classList.remove('hidden');
    stdinDrawer?.classList.add('hidden');
    pythonHeader?.classList.add('hidden');
    webHeader?.classList.remove('hidden');
    pythonOutput?.classList.add('hidden');

    switchWebSubtab('preview');

    document.querySelectorAll('#pg-web-file-tabs .file-tab').forEach(t => {
      t.classList.toggle('active', t.dataset.file === 'html');
    });

    if (editor) {
      editor.setOption('mode', 'htmlmixed');
      editor.setValue(webFiles.html);
    }

    runPlaygroundCode();
  } else {
    currentLang = 'python';
    pythonCode = prog.code || '';

    // Update Language Tabs UI
    document.querySelectorAll('#pg-lang-tabs .lang-tab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.lang === 'python');
    });

    const webFileTabs = document.getElementById('pg-web-file-tabs');
    const templateSelect = document.getElementById('pg-template-select');
    const stdinDrawer = document.getElementById('pg-stdin-drawer');
    const pythonHeader = document.getElementById('pg-python-console-header');
    const webHeader = document.getElementById('pg-web-console-header');
    const pythonOutput = document.getElementById('pg-console-output');
    const webPreview = document.getElementById('pg-web-preview-container');
    const browserConsole = document.getElementById('pg-browser-console-list');
    const topbarTitle = document.getElementById('topbar-title');

    if (topbarTitle) topbarTitle.textContent = `Python Code Playground — ${prog.title}`;
    webFileTabs?.classList.add('hidden');
    templateSelect?.classList.add('hidden');
    stdinDrawer?.classList.remove('hidden');
    pythonHeader?.classList.remove('hidden');
    webHeader?.classList.add('hidden');
    pythonOutput?.classList.remove('hidden');
    webPreview?.classList.add('hidden');
    browserConsole?.classList.add('hidden');

    if (editor) {
      editor.setOption('mode', 'python');
      editor.setValue(pythonCode);
    }
  }

  if (editor && editor.refresh) {
    editor.refresh();
    setTimeout(() => editor.refresh(), 80);
  }

  const libModal = document.getElementById('pg-library-modal');
  if (libModal) {
    libModal.classList.add('hidden');
  }

  showToast(`Opened project "${prog.title}" into workspace!`, 'success');
}

init();
