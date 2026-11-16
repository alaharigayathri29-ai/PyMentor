import { workspaceApi, getUser } from './api.js?v=20261108_v17';
import { showToast, navigate } from './app.js?v=20261108_v17';

let editor = null;
let currentMode = 'web'; // 'web' | 'python' | 'javascript'
let currentWebTab = 'html'; // 'html' | 'css' | 'js'
let currentProgramId = null;
let currentProgramTitle = 'Untitled Web Project';
let savedPrograms = [];
let autoRenderTimer = null;

// Multi-file memory for Web Studio
let webFiles = {
  html: `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My Web Project</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="card">
    <div class="badge">🌐 Interactive Web App</div>
    <h1>Hello, World!</h1>
    <p>Build stunning HTML, CSS, and JavaScript websites with real-time live preview.</p>
    
    <div class="counter-box">
      <button id="dec-btn" class="btn btn-secondary">-</button>
      <span id="counter-val">0</span>
      <button id="inc-btn" class="btn btn-primary">+</button>
    </div>

    <button id="color-btn" class="btn btn-gradient">✨ Change Theme Color</button>
  </div>

  <script src="script.js"></script>
</body>
</html>`,
  css: `/* Modern Glassmorphic Styling */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Inter', system-ui, sans-serif;
  background: radial-gradient(circle at top left, #1e1b4b, #0f172a, #020617);
  color: #f8fafc;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 20px;
  padding: 36px 32px;
  max-width: 440px;
  width: 100%;
  text-align: center;
  backdrop-filter: blur(16px);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
  transition: transform 0.3s ease;
}

.card:hover {
  transform: translateY(-4px);
}

.badge {
  display: inline-block;
  background: rgba(124, 58, 237, 0.2);
  color: #c084fc;
  border: 1px solid rgba(124, 58, 237, 0.4);
  padding: 4px 14px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 16px;
}

h1 {
  font-size: 28px;
  font-weight: 800;
  margin-bottom: 10px;
  background: linear-gradient(135deg, #a855f7, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

p {
  color: #94a3b8;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 24px;
}

.counter-box {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 20px;
}

#counter-val {
  font-size: 32px;
  font-weight: 800;
  min-width: 50px;
  color: #38bdf8;
}

.btn {
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
}

.btn:active {
  transform: scale(0.95);
}

.btn-primary {
  background: #7c3aed;
  color: white;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #e2e8f0;
}

.btn-gradient {
  width: 100%;
  background: linear-gradient(135deg, #7c3aed, #06b6d4);
  color: white;
  margin-top: 10px;
  box-shadow: 0 4px 20px rgba(124, 58, 237, 0.35);
}`,
  js: `// Interactive JavaScript logic
let count = 0;
const counterVal = document.getElementById('counter-val');
const incBtn = document.getElementById('inc-btn');
const decBtn = document.getElementById('dec-btn');
const colorBtn = document.getElementById('color-btn');

incBtn.addEventListener('click', () => {
  count++;
  counterVal.textContent = count;
  console.log('Count incremented to:', count);
});

decBtn.addEventListener('click', () => {
  count--;
  counterVal.textContent = count;
  console.log('Count decremented to:', count);
});

const gradients = [
  'radial-gradient(circle at top left, #1e1b4b, #0f172a, #020617)',
  'radial-gradient(circle at top left, #311042, #180924, #08030d)',
  'radial-gradient(circle at top left, #052e2b, #041f1e, #020b0b)',
  'radial-gradient(circle at top left, #3b0764, #1e1035, #08030f)'
];
let gradIdx = 0;

colorBtn.addEventListener('click', () => {
  gradIdx = (gradIdx + 1) % gradients.length;
  document.body.style.background = gradients[gradIdx];
  console.log('Theme changed to gradient index:', gradIdx);
});

console.log('🚀 Web App initialized successfully!');`
};

let pythonScript = `# Python 3.10 Interactive Playground
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

print("First 10 Fibonacci numbers:")
print(list(fibonacci(10)))
`;

// Starter templates
const STARTER_TEMPLATES = [
  {
    id: 'web-portfolio',
    language: 'web',
    title: 'Modern Glassmorphic Card',
    desc: 'HTML5, CSS3 Glassmorphism with interactive theme toggle',
    data: { ...webFiles }
  },
  {
    id: 'web-calculator',
    language: 'web',
    title: 'Neon Web Calculator',
    desc: 'CSS Grid calculator with animated keypresses',
    data: {
      html: `<!DOCTYPE html>
<html>
<head>
  <title>Neon Calculator</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="calc">
    <div id="screen" class="screen">0</div>
    <div class="buttons">
      <button class="btn op" onclick="clearCalc()">C</button>
      <button class="btn op" onclick="press('/')">÷</button>
      <button class="btn op" onclick="press('*')">×</button>
      <button class="btn op" onclick="delChar()">⌫</button>
      
      <button class="btn" onclick="press('7')">7</button>
      <button class="btn" onclick="press('8')">8</button>
      <button class="btn" onclick="press('9')">9</button>
      <button class="btn op" onclick="press('-')">-</button>

      <button class="btn" onclick="press('4')">4</button>
      <button class="btn" onclick="press('5')">5</button>
      <button class="btn" onclick="press('6')">6</button>
      <button class="btn op" onclick="press('+')">+</button>

      <button class="btn" onclick="press('1')">1</button>
      <button class="btn" onclick="press('2')">2</button>
      <button class="btn" onclick="press('3')">3</button>
      <button class="btn eq" onclick="calculate()">=</button>

      <button class="btn zero" onclick="press('0')">0</button>
      <button class="btn" onclick="press('.')">.</button>
    </div>
  </div>
  <script src="script.js"></script>
</body>
</html>`,
      css: `body {
  background: #080711;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  font-family: 'JetBrains Mono', monospace;
  margin: 0;
}
.calc {
  background: #121024;
  border: 1px solid rgba(124, 58, 237, 0.3);
  box-shadow: 0 10px 40px rgba(124, 58, 237, 0.2);
  border-radius: 16px;
  padding: 24px;
  width: 320px;
}
.screen {
  background: #06050d;
  color: #38bdf8;
  font-size: 32px;
  padding: 16px;
  border-radius: 10px;
  text-align: right;
  margin-bottom: 20px;
  border: 1px solid rgba(255,255,255,0.06);
  min-height: 70px;
  overflow-x: auto;
}
.buttons {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}
.btn {
  background: rgba(255,255,255,0.04);
  color: #f1f5f9;
  border: 1px solid rgba(255,255,255,0.08);
  font-size: 18px;
  padding: 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}
.btn:hover { background: rgba(124,58,237,0.2); border-color: #7c3aed; }
.btn.op { color: #c084fc; font-weight: bold; }
.btn.eq { background: #7c3aed; color: #fff; grid-row: span 2; height: 100%; }
.btn.zero { grid-column: span 2; }`,
      js: `let expr = '';
const screen = document.getElementById('screen');

function press(val) {
  if (screen.textContent === '0' && val !== '.') expr = '';
  expr += val;
  screen.textContent = expr;
  console.log('Input:', val, '| Current expr:', expr);
}
function clearCalc() {
  expr = '';
  screen.textContent = '0';
}
function delChar() {
  expr = expr.slice(0, -1);
  screen.textContent = expr || '0';
}
function calculate() {
  try {
    const result = Function('"use strict";return (' + expr + ')')();
    screen.textContent = result;
    console.log('Result of', expr, '=', result);
    expr = String(result);
  } catch (err) {
    screen.textContent = 'Error';
    console.error('Calculation error:', err);
    expr = '';
  }
}`
    }
  },
  {
    id: 'py-basics',
    language: 'python',
    title: 'Python: Data Structures & Math',
    desc: 'List comprehensions, dictionaries, and math operations',
    code: `# Python 3.10 practice
numbers = [1, 4, 9, 16, 25, 36, 49, 64]
roots = {n: int(n**0.5) for n in numbers}

print("Number -> Square Root mapping:")
for num, root in roots.items():
    print(f"  {num:>2} -> {root}")
`
  }
];

export async function initWorkspace() {
  currentProgramId = null;
  renderWorkspaceLayout();
  initEditor();
  await loadSavedPrograms();

  if (savedPrograms && savedPrograms.length > 0) {
    // Automatically load the logged-in student's project!
    await loadSavedProject(savedPrograms[0].id);
  } else {
    // Start with a clean project personalized for this student
    newProject(false);
  }
}

function renderWorkspaceLayout() {
  document.getElementById('page-workspace').innerHTML = `
    <div class="page-content" style="height:calc(100vh - var(--topbar-h) - 48px);min-height:560px;display:flex;flex-direction:column;padding:16px 24px">
      
      <!-- Top Workspace Bar -->
      <div class="section-header" style="flex-shrink:0;margin-bottom:12px">
        <div>
          <div style="display:flex;align-items:center;gap:12px">
            <h1 class="page-title" style="margin-bottom:0">Code Studio & Playground</h1>
            
            <!-- Language Mode Selector Dropdown -->
            <div class="lang-selector-wrap">
              <select id="ws-lang-select" class="form-input" style="padding:5px 12px;font-size:13px;width:auto;font-weight:600;background:rgba(124,58,237,0.15);border-color:rgba(124,58,237,0.4);color:var(--text-accent)" onchange="onLanguageModeChange(this.value)">
                <option value="web">🌐 Web (HTML / CSS / JS)</option>
                <option value="python">🐍 Python 3.10</option>
              </select>
            </div>
          </div>
          <p class="page-sub" style="margin-bottom:0;margin-top:3px" id="ws-mode-desc">
            Build full websites with HTML, CSS, JavaScript and live interactive browser preview.
          </p>
        </div>

        <!-- Action Buttons -->
        <div style="display:flex;align-items:center;gap:8px">
          <button class="btn btn-ghost btn-sm" id="ws-toggle-sidebar-btn" onclick="toggleWorkspaceSidebar()" title="Toggle Library Sidebar">
            <span id="ws-sidebar-btn-icon">◀</span> Library
          </button>
          <button class="btn btn-ghost btn-sm" onclick="newProject()">📄 New</button>
          <button class="btn btn-secondary btn-sm" onclick="openSaveModal()">💾 Save</button>
          <button class="btn btn-secondary btn-sm" id="ws-fs-btn" onclick="openFullscreenApp()" style="background:rgba(124,58,237,0.15);border:1px solid rgba(124,58,237,0.4);color:var(--text-accent);" title="Open Project in Fullscreen HTML">
            <span>🖥️</span> Fullscreen Preview
          </button>
          <button class="btn btn-primary btn-sm" id="ws-run-btn" onclick="executeCurrentCode()">
            <span id="ws-run-icon">▶</span> <span id="ws-run-label">Run & Render</span> <span style="font-size:11px;opacity:0.8">(Ctrl+Enter)</span>
          </button>
        </div>
      </div>

      <!-- Main Workspace Grid (Left Library | Right Code & Browser/Terminal) -->
      <div class="workspace-grid" id="ws-main-grid" style="flex:1;min-height:0;display:grid;grid-template-columns:260px 1fr;gap:16px">
        
        <!-- Left Sidebar: Saved Library & Starter Templates -->
        <div class="workspace-sidebar" id="ws-sidebar-panel" style="background:var(--bg-card);border:1px solid var(--border);border-radius:var(--r-lg);display:flex;flex-direction:column;overflow:hidden">
          
          <div style="padding:12px 16px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center">
            <span style="font-size:12px;font-weight:700;letter-spacing:0.04em">SAVED PROJECTS</span>
            <span class="badge badge-gray" id="ws-prog-count">0 items</span>
          </div>

          <div style="display:flex;padding:6px;background:rgba(255,255,255,0.02);border-bottom:1px solid var(--border)">
            <button class="auth-tab active" id="ws-tab-saved" style="padding:5px;font-size:11px" onclick="switchSidebarTab('saved')">My Projects</button>
            <button class="auth-tab" id="ws-tab-templates" style="padding:5px;font-size:11px" onclick="switchSidebarTab('templates')">Templates</button>
          </div>

          <div id="ws-programs-list" style="flex:1;overflow-y:auto;padding:8px">
            <div class="flex-center" style="padding:30px;color:var(--text-muted);font-size:12px">Loading projects…</div>
          </div>

          <div id="ws-templates-list" class="hidden" style="flex:1;overflow-y:auto;padding:8px">
            ${STARTER_TEMPLATES.map(t => `
              <div class="ws-program-item" onclick="loadStarterTemplate('${t.id}')">
                <div style="display:flex;align-items:center;gap:6px">
                  <span>${t.language === 'web' ? '🌐' : '🐍'}</span>
                  <div style="font-weight:600;font-size:12.5px;color:var(--text-primary)">${t.title}</div>
                </div>
                <div style="font-size:11px;color:var(--text-muted);margin-top:2px">${t.desc}</div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Right Main Workspace: Editor on Left, Live Browser / Terminal on Right (Split View) -->
        <div class="workspace-editor-stage" style="display:grid;grid-template-columns:1fr 1fr;gap:14px;min-height:0">
          
          <!-- Code Editor Panel -->
          <div class="editor-panel" style="display:flex;flex-direction:column;overflow:hidden;background:var(--bg-card);border:1px solid var(--border);border-radius:var(--r-lg)">
            
            <!-- File Tabs for Web Mode / Language Header for Python -->
            <div class="editor-toolbar" style="padding:8px 12px">
              
              <!-- Web Multi-File Tabs -->
              <div id="ws-web-tabs" style="display:flex;gap:4px">
                <button class="ws-file-tab active" id="tab-html" onclick="switchWebFileTab('html')">
                  <span>📄</span> index.html
                </button>
                <button class="ws-file-tab" id="tab-css" onclick="switchWebFileTab('css')">
                  <span>🎨</span> style.css
                </button>
                <button class="ws-file-tab" id="tab-js" onclick="switchWebFileTab('js')">
                  <span>⚡</span> script.js
                </button>
              </div>

              <!-- Python Mode Single Header -->
              <div id="ws-py-header" class="hidden" style="display:flex;align-items:center;gap:8px">
                <span class="editor-lang-badge">main.py</span>
                <span id="ws-current-title" style="font-size:13px;font-weight:600;color:var(--text-primary)">Untitled Script</span>
              </div>

              <!-- Editor Right Actions -->
              <div style="display:flex;gap:4px;align-items:center">
                <button class="btn btn-ghost btn-sm" style="padding:3px 8px;font-size:11px" onclick="copyCurrentCode()" title="Copy active file">📋 Copy</button>
                <button class="btn btn-ghost btn-sm" style="padding:3px 8px;font-size:11px" onclick="downloadProjectBundle()" title="Download file">⬇ Export</button>
                <button class="btn btn-ghost btn-sm" style="padding:3px 8px;font-size:11px" onclick="clearCurrentEditor()" title="Clear editor">🗑</button>
              </div>
            </div>

            <!-- CodeMirror Editor Box -->
            <div class="editor-wrap" id="ws-editor-wrap" style="flex:1;overflow:hidden">
              <textarea id="ws-main-editor" style="display:none"></textarea>
            </div>
          </div>

          <!-- Right Stage: Live Interactive Browser Window (or Terminal in Python Mode) -->
          <div class="preview-panel" style="display:flex;flex-direction:column;overflow:hidden;background:#0d0d18;border:1px solid var(--border);border-radius:var(--r-lg)">
            
            <!-- Browser Chrome Header Bar -->
            <div class="browser-chrome" id="browser-chrome-bar" style="padding:8px 12px;background:rgba(255,255,255,0.03);border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;gap:8px">
              
              <!-- Window Dots & Title -->
              <div style="display:flex;align-items:center;gap:6px">
                <div style="width:10px;height:10px;border-radius:50%;background:#ef4444"></div>
                <div style="width:10px;height:10px;border-radius:50%;background:#f59e0b"></div>
                <div style="width:10px;height:10px;border-radius:50%;background:#10b981"></div>
                <span style="font-size:11px;font-weight:700;color:var(--text-secondary);margin-left:6px" id="ws-stage-title">BROWSER PREVIEW</span>
              </div>

              <!-- Simulated URL Address Bar (for Web Mode) -->
              <div id="ws-browser-address" style="flex:1;max-width:240px;background:rgba(0,0,0,0.4);border:1px solid var(--border);border-radius:6px;padding:3px 10px;font-size:11px;color:#94a3b8;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">
                <span>🔒</span> https://preview.local/
              </div>

              <!-- Viewport Sizing & Console Toggle (for Web Mode) -->
              <div style="display:flex;gap:4px;align-items:center" id="ws-browser-controls">
                <button class="btn btn-ghost btn-sm" style="padding:2px 8px;font-size:11px" onclick="renderLivePreview()" title="Reload preview">↺ Refresh</button>
                <button class="btn btn-ghost btn-sm" id="ws-toggle-console-btn" style="padding:2px 8px;font-size:11px" onclick="toggleWebConsole()">Console</button>
                <button class="btn btn-ghost btn-sm" style="padding:2px 8px;font-size:11px;color:var(--cyan);font-weight:600;" onclick="openFullscreenApp()" title="Open in Fullscreen HTML View">⛶ Fullscreen</button>
              </div>

              <!-- Terminal Controls (for Python Mode) -->
              <div style="display:flex;gap:6px;align-items:center" id="ws-terminal-controls" class="hidden">
                <span id="ws-exec-badge" class="badge badge-gray" style="font-size:10px">Ready</span>
                <span id="ws-exec-time" style="font-size:11px;color:var(--text-muted)"></span>
                <input id="ws-stdin-input" type="text" placeholder="stdin input..." class="form-input" style="width:110px;padding:2px 6px;font-size:11px;height:22px" />
                <button class="btn btn-ghost btn-sm" style="padding:2px 6px;font-size:10px" onclick="clearTerminalOutput()">Clear</button>
              </div>
            </div>

            <!-- Web Mode Live Iframe Preview -->
            <div id="ws-preview-container" style="flex:1;display:flex;flex-direction:column;overflow:hidden;background:#fff;position:relative">
              <iframe id="ws-live-frame" style="width:100%;height:100%;border:none;background:#fff" sandbox="allow-scripts allow-modals allow-same-origin"></iframe>
              
              <!-- Bottom Web Console Drawer (collapsible) -->
              <div id="ws-web-console" class="hidden" style="height:120px;background:#090910;border-top:1px solid var(--border);display:flex;flex-direction:column;position:absolute;bottom:0;left:0;right:0;z-index:10">
                <div style="padding:4px 10px;background:rgba(255,255,255,0.03);display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,255,255,0.06)">
                  <span style="font-size:11px;font-weight:700;color:var(--text-secondary)">DEV CONSOLE</span>
                  <button class="btn btn-ghost btn-sm" style="padding:1px 6px;font-size:10px" onclick="clearWebConsole()">Clear</button>
                </div>
                <div id="ws-console-logs" style="flex:1;overflow-y:auto;padding:8px 12px;font-family:'JetBrains Mono',monospace;font-size:11px;line-height:1.5;color:#94a3b8">
                  <span style="color:var(--text-muted)">Console output will appear here...</span>
                </div>
              </div>
            </div>

            <!-- Python Mode Terminal Output -->
            <div id="ws-python-terminal" class="hidden" style="flex:1;padding:14px;overflow-y:auto;font-family:'JetBrains Mono',monospace;font-size:13px;line-height:1.6;color:#94a3b8;white-space:pre-wrap;background:#080812">
              <span style="color:var(--text-muted)">Click "Run Code" or press Ctrl+Enter to execute Python...</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Save Project Modal -->
    <div id="ws-save-modal" class="modal-overlay hidden">
      <div class="modal-box" style="width:420px;background:var(--bg-sidebar);border:1px solid var(--border);border-radius:var(--r-xl);padding:24px;box-shadow:var(--shadow-card)">
        <h3 style="font-size:18px;font-weight:700;margin-bottom:6px">Save Project to Library</h3>
        <p style="font-size:13px;color:var(--text-secondary);margin-bottom:20px">Save your HTML/CSS/JS website or Python program for future practice.</p>
        
        <div class="form-group">
          <label class="form-label">Project Title</label>
          <input id="ws-modal-title" class="form-input" type="text" placeholder="e.g. Interactive Portfolio" maxlength="100" required />
        </div>
        
        <div class="form-group">
          <label class="form-label">Description (optional)</label>
          <textarea id="ws-modal-desc" class="form-input" rows="2" placeholder="Notes or features implemented..."></textarea>
        </div>

        <div style="display:flex;justify-content:flex-end;gap:10px;margin-top:20px">
          <button class="btn btn-ghost btn-sm" onclick="closeSaveModal()">Cancel</button>
          <button class="btn btn-primary btn-sm" id="ws-modal-save-btn" onclick="confirmSaveProject()">Save to Library</button>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════════════════════ -->
    <!--  FULLSCREEN HTML LIVE PREVIEW OVERLAY                                      -->
    <!-- ═══════════════════════════════════════════════════════════════════════════ -->
    <div id="ws-fullscreen-overlay" class="hidden" style="position:fixed;inset:0;z-index:99999;background:#06080f;display:none;flex-direction:column;">
      <div style="height:56px;background:#0d111c;border-bottom:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:space-between;padding:0 20px;flex-shrink:0;">
        <div style="display:flex;align-items:center;gap:10px;">
          <button class="btn btn-secondary btn-sm" onclick="closeFullscreenApp()" style="display:flex;align-items:center;gap:6px;font-weight:700;background:rgba(255,255,255,0.08);color:#fff;">
            <span>←</span> Back to Studio
          </button>
          <button class="btn btn-ghost btn-sm" onclick="closeFullscreenApp(); navigateTo('dashboard');" style="display:flex;align-items:center;gap:6px;color:#94a3b8;">
            <span>🏠</span> Back to Home
          </button>
        </div>
        <div style="display:flex;align-items:center;gap:10px;">
          <span style="display:inline-flex;align-items:center;gap:6px;background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.3);color:#34d399;padding:3px 10px;border-radius:9999px;font-size:11px;font-weight:700;">
            <span style="width:6px;height:6px;border-radius:50%;background:#10b981;"></span>
            LIVE HTML APP
          </span>
          <span id="ws-fs-title" style="font-size:14px;font-weight:700;color:#f1f5f9;max-width:320px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
            Untitled Project
          </span>
        </div>
        <div style="display:flex;align-items:center;gap:8px;">
          <div style="display:flex;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:8px;padding:2px;">
            <button class="btn btn-ghost btn-sm" onclick="setFullscreenViewport('100%')" style="padding:2px 8px;font-size:11px;">🖥️ Full</button>
            <button class="btn btn-ghost btn-sm" onclick="setFullscreenViewport('768px')" style="padding:2px 8px;font-size:11px;">📱 768px</button>
            <button class="btn btn-ghost btn-sm" onclick="setFullscreenViewport('390px')" style="padding:2px 8px;font-size:11px;">📱 390px</button>
          </div>
          <button class="btn btn-ghost btn-sm" onclick="refreshFullscreenApp()" title="Reload Frame">↺</button>
          <button class="btn btn-ghost btn-sm" onclick="closeFullscreenApp()" style="font-size:16px;padding:2px 8px;" title="Close Fullscreen (Esc)">✕</button>
        </div>
      </div>
      <div id="ws-fs-frame-container" style="flex:1;display:flex;align-items:center;justify-content:center;background:#05070e;overflow:hidden;position:relative;">
        <iframe id="ws-fullscreen-frame" style="width:100%;height:100%;border:none;background:#fff;transition:width 0.3s ease;" sandbox="allow-scripts allow-modals allow-same-origin"></iframe>
      </div>
    </div>
  `;

  // Attach window event handlers
  window.toggleWorkspaceSidebar= toggleWorkspaceSidebar;
  window.onLanguageModeChange   = onLanguageModeChange;
  window.switchWebFileTab       = switchWebFileTab;
  window.switchSidebarTab       = switchSidebarTab;
  window.loadStarterTemplate    = loadStarterTemplate;
  window.loadSavedProject       = loadSavedProject;
  window.deleteSavedProject     = deleteSavedProject;
  window.newProject             = newProject;
  window.executeCurrentCode     = executeCurrentCode;
  window.renderLivePreview      = renderLivePreview;
  window.toggleWebConsole       = toggleWebConsole;
  window.clearWebConsole        = clearWebConsole;
  window.clearTerminalOutput    = clearTerminalOutput;
  window.copyCurrentCode        = copyCurrentCode;
  window.downloadProjectBundle  = downloadProjectBundle;
  window.clearCurrentEditor     = clearCurrentEditor;
  window.openSaveModal          = openSaveModal;
  window.closeSaveModal         = closeSaveModal;
  window.confirmSaveProject     = confirmSaveProject;
  window.openFullscreenApp      = openFullscreenApp;
  window.closeFullscreenApp     = closeFullscreenApp;
  window.refreshFullscreenApp   = refreshFullscreenApp;
  window.setFullscreenViewport  = setFullscreenViewport;
}

let sidebarOpen = true;
function toggleWorkspaceSidebar() {
  sidebarOpen = !sidebarOpen;
  const sidebarEl = document.getElementById('ws-sidebar-panel');
  const gridEl = document.getElementById('ws-main-grid');
  const iconEl = document.getElementById('ws-sidebar-btn-icon');
  if (sidebarEl && gridEl) {
    sidebarEl.style.display = sidebarOpen ? 'flex' : 'none';
    gridEl.style.gridTemplateColumns = sidebarOpen ? '260px 1fr' : '1fr';
    if (iconEl) iconEl.textContent = sidebarOpen ? '◀' : '▶';
    if (editor) setTimeout(() => editor.refresh(), 50);
  }
}

// ── Editor Initialization ─────────────────────────────────────────────────────
function initEditor() {
  const modeSpec = currentMode === 'web'
    ? (currentWebTab === 'html' ? 'htmlmixed' : currentWebTab === 'css' ? 'css' : 'javascript')
    : 'python';

  const initialCode = currentMode === 'web' ? webFiles[currentWebTab] : pythonScript;

  if (window.CodeMirror) {
    if (editor) { editor.toTextArea(); editor = null; }
    editor = window.CodeMirror.fromTextArea(document.getElementById('ws-main-editor'), {
      mode: modeSpec,
      theme: 'dracula',
      lineNumbers: true,
      indentUnit: 2,
      tabSize: 2,
      indentWithTabs: false,
      matchBrackets: true,
      autoCloseBrackets: true,
      lineWrapping: false,
      extraKeys: {
        'Tab': (cm) => cm.replaceSelection('  '),
        'Ctrl-Enter': () => executeCurrentCode(),
        'Cmd-Enter': () => executeCurrentCode(),
        'Ctrl-S': (cm) => { openSaveModal(); },
        'Cmd-S': (cm) => { openSaveModal(); },
      },
    });

    editor.setValue(initialCode || '');

    // Auto-update live preview on typing (debounced)
    editor.on('change', () => {
      saveEditorToMemory();
      if (currentMode === 'web') {
        clearTimeout(autoRenderTimer);
        autoRenderTimer = setTimeout(() => {
          renderLivePreview();
        }, 600);
      }
    });

    setTimeout(() => editor.refresh(), 100);
  } else {
    const ta = document.getElementById('ws-main-editor');
    ta.style.display = 'block';
    ta.style.cssText += ';width:100%;height:100%;background:#0d0d18;color:#f1f5f9;border:none;padding:16px;font-family:JetBrains Mono,monospace;font-size:13px;resize:none;outline:none;';
    ta.value = initialCode || '';
    ta.addEventListener('input', () => {
      saveEditorToMemory();
      if (currentMode === 'web') renderLivePreview();
    });
  }
}

function saveEditorToMemory() {
  const code = editor ? editor.getValue() : document.getElementById('ws-main-editor')?.value || '';
  if (currentMode === 'web') {
    webFiles[currentWebTab] = code;
  } else {
    pythonScript = code;
  }
}

// ── Language Mode Switching ───────────────────────────────────────────────────
function onLanguageModeChange(mode) {
  saveEditorToMemory();
  currentMode = mode;

  const webTabs = document.getElementById('ws-web-tabs');
  const pyHeader = document.getElementById('ws-py-header');
  const descEl = document.getElementById('ws-mode-desc');
  const stageTitle = document.getElementById('ws-stage-title');
  const browserAddress = document.getElementById('ws-browser-address');
  const browserControls = document.getElementById('ws-browser-controls');
  const terminalControls = document.getElementById('ws-terminal-controls');
  const previewContainer = document.getElementById('ws-preview-container');
  const pythonTerminal = document.getElementById('ws-python-terminal');
  const runLabel = document.getElementById('ws-run-label');

  if (mode === 'web') {
    webTabs.style.display = 'flex';
    pyHeader.style.display = 'none';
    descEl.textContent = 'Build full websites with HTML, CSS, JavaScript and live interactive browser preview.';
    stageTitle.textContent = 'BROWSER PREVIEW';
    browserAddress.style.display = 'block';
    browserControls.style.display = 'flex';
    terminalControls.style.display = 'none';
    previewContainer.style.display = 'flex';
    pythonTerminal.style.display = 'none';
    runLabel.textContent = 'Render Preview';
    
    switchWebFileTab(currentWebTab);
    renderLivePreview();
  } else {
    webTabs.style.display = 'none';
    pyHeader.style.display = 'flex';
    descEl.textContent = 'Write and execute Python 3.10 code with real-time console stdout/stderr output.';
    stageTitle.textContent = 'OUTPUT TERMINAL';
    browserAddress.style.display = 'none';
    browserControls.style.display = 'none';
    terminalControls.style.display = 'flex';
    previewContainer.style.display = 'none';
    pythonTerminal.style.display = 'block';
    runLabel.textContent = 'Run Python';

    if (editor) {
      editor.setOption('mode', 'python');
      editor.setValue(pythonScript);
    }
  }
}

// ── Web File Tabs ─────────────────────────────────────────────────────────────
function switchWebFileTab(tab) {
  saveEditorToMemory();
  currentWebTab = tab;

  document.getElementById('tab-html')?.classList.toggle('active', tab === 'html');
  document.getElementById('tab-css')?.classList.toggle('active', tab === 'css');
  document.getElementById('tab-js')?.classList.toggle('active', tab === 'js');

  const modeMap = { html: 'htmlmixed', css: 'css', js: 'javascript' };
  if (editor) {
    editor.setOption('mode', modeMap[tab] || 'htmlmixed');
    editor.setValue(webFiles[tab] || '');
    editor.refresh();
  }
}

// ── Live Browser Preview Rendering ────────────────────────────────────────────
function renderLivePreview() {
  if (currentMode !== 'web') return;
  saveEditorToMemory();

  const iframe = document.getElementById('ws-live-frame');
  if (!iframe) return;

  // Intercept console.log and errors from iframe
  const consoleScript = `
    <script>
      (function() {
        const _log = console.log;
        const _error = console.error;
        const _warn = console.warn;
        
        function sendLog(type, args) {
          window.parent.postMessage({
            type: 'IFRAME_CONSOLE',
            level: type,
            message: Array.from(args).map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' ')
          }, '*');
        }

        console.log = function() { sendLog('log', arguments); _log.apply(console, arguments); };
        console.error = function() { sendLog('error', arguments); _error.apply(console, arguments); };
        console.warn = function() { sendLog('warn', arguments); _warn.apply(console, arguments); };
        
        window.onerror = function(msg, url, line) {
          sendLog('error', ['Uncaught Error: ' + msg + ' (line ' + line + ')']);
        };
      })();
    <\/script>
  `;

  let htmlContent = webFiles.html || '';

  // Inject CSS inside <head> or at top
  const cssBlock = `<style>\n${webFiles.css || ''}\n</style>`;
  if (htmlContent.includes('</head>')) {
    htmlContent = htmlContent.replace('</head>', `${cssBlock}\n</head>`);
  } else {
    htmlContent = `${cssBlock}\n${htmlContent}`;
  }

  // Inject JS at bottom of body
  const jsBlock = `${consoleScript}\n<script>\n${webFiles.js || ''}\n<\/script>`;
  if (htmlContent.includes('</body>')) {
    htmlContent = htmlContent.replace('</body>', `${jsBlock}\n</body>`);
  } else {
    htmlContent = `${htmlContent}\n${jsBlock}`;
  }

  iframe.srcdoc = htmlContent;
}

// Listen for console messages from preview iframe
window.addEventListener('message', (e) => {
  if (e.data && e.data.type === 'IFRAME_CONSOLE') {
    appendWebConsoleLog(e.data.level, e.data.message);
  }
});

function appendWebConsoleLog(level, msg) {
  const container = document.getElementById('ws-console-logs');
  if (!container) return;

  const placeholder = container.querySelector('span');
  if (placeholder && placeholder.textContent.includes('Console output')) {
    placeholder.remove();
  }

  const row = document.createElement('div');
  row.style.marginBottom = '4px';
  row.style.display = 'flex';
  row.style.gap = '8px';

  const badge = document.createElement('span');
  badge.style.fontSize = '10px';
  badge.style.padding = '1px 5px';
  badge.style.borderRadius = '3px';

  if (level === 'error') {
    badge.textContent = 'ERR';
    badge.style.background = 'rgba(239,68,68,0.2)';
    badge.style.color = '#f87171';
    row.style.color = '#f87171';
  } else if (level === 'warn') {
    badge.textContent = 'WARN';
    badge.style.background = 'rgba(245,158,11,0.2)';
    badge.style.color = '#fbbf24';
    row.style.color = '#fbbf24';
  } else {
    badge.textContent = 'LOG';
    badge.style.background = 'rgba(59,130,246,0.2)';
    badge.style.color = '#60a5fa';
    row.style.color = '#f1f5f9';
  }

  const text = document.createElement('span');
  text.textContent = msg;

  row.appendChild(badge);
  row.appendChild(text);
  container.appendChild(row);
  container.scrollTop = container.scrollHeight;
}

function toggleWebConsole() {
  const consoleEl = document.getElementById('ws-web-console');
  const btn = document.getElementById('ws-toggle-console-btn');
  const isHidden = consoleEl.classList.toggle('hidden');
  btn.classList.toggle('active', !isHidden);
}

function clearWebConsole() {
  const container = document.getElementById('ws-console-logs');
  if (container) container.innerHTML = '<span style="color:var(--text-muted)">Console cleared.</span>';
}

// ── Python Code Execution ─────────────────────────────────────────────────────
async function executeCurrentCode() {
  if (currentMode === 'web') {
    renderLivePreview();
    showToast('Live preview rendered! 🌐', 'success');
    const stageTitle = document.getElementById('ws-stage-title');
    if (stageTitle) {
      stageTitle.textContent = '✓ PREVIEW UPDATED';
      setTimeout(() => { stageTitle.textContent = 'BROWSER PREVIEW'; }, 1500);
    }
    return;
  }

  // Python mode
  saveEditorToMemory();
  const code = pythonScript.trim();
  if (!code) { showToast('Please write some Python code first!', 'warn'); return; }

  const stdinInput = document.getElementById('ws-stdin-input')?.value || '';
  const runBtn = document.getElementById('ws-run-btn');
  const badgeEl = document.getElementById('ws-exec-badge');
  const timeEl = document.getElementById('ws-exec-time');
  const outputEl = document.getElementById('ws-python-terminal');

  runBtn.disabled = true;
  runBtn.innerHTML = '<span class="loading-spin">⟳</span> Running…';
  badgeEl.className = 'badge badge-amber';
  badgeEl.textContent = 'Executing…';
  timeEl.textContent = '';
  outputEl.innerHTML = '<div style="color:var(--text-muted);font-family:inherit">>>> Running Python 3.10 script...</div>';

  try {
    const result = await workspaceApi.runCode(code, stdinInput);
    timeEl.textContent = `${result.execution_time_ms} ms`;

    if (result.success) {
      badgeEl.className = 'badge badge-green';
      badgeEl.textContent = '✓ Success (0)';
      outputEl.innerHTML = `
        <div style="color:#60a5fa;font-weight:600;font-size:11px;margin-bottom:8px">>>> Process finished with exit code 0 (${result.execution_time_ms} ms)</div>
        <div style="white-space:pre-wrap;color:#34d399;font-family:inherit">${escapeHtml(result.stdout || 'Program completed with no output.')}</div>
      `;
    } else {
      badgeEl.className = 'badge badge-red';
      badgeEl.textContent = '✕ Error';
      const errText = result.stderr || result.error || 'Execution failed.';
      outputEl.innerHTML = `
        <div style="color:#ef4444;font-weight:600;font-size:11px;margin-bottom:8px">>>> Process exited with errors (${result.execution_time_ms} ms)</div>
        <div style="white-space:pre-wrap;color:#f87171;font-family:inherit">${escapeHtml(errText)}</div>
        ${result.stdout ? `<div style="color:#60a5fa;font-weight:600;font-size:11px;margin-top:12px;margin-bottom:6px">>>> Standard Output:</div><div style="white-space:pre-wrap;color:#94a3b8;font-family:inherit">${escapeHtml(result.stdout)}</div>` : ''}
      `;
    }
    outputEl.scrollTop = outputEl.scrollHeight;
  } catch (err) {
    badgeEl.className = 'badge badge-red';
    badgeEl.textContent = '✕ Network Error';
    outputEl.innerHTML = `<div style="color:#f87171;font-family:inherit">>>> Error communicating with server: ${escapeHtml(err.message)}</div>`;
  } finally {
    runBtn.disabled = false;
    runBtn.innerHTML = '<span id="ws-run-icon">▶</span> <span id="ws-run-label">Run Python</span> <span style="font-size:11px;opacity:0.8">(Ctrl+Enter)</span>';
  }
}

function clearTerminalOutput() {
  const el = document.getElementById('ws-python-terminal');
  if (el) {
    el.innerHTML = '<span style="color:var(--text-muted)">Terminal cleared.</span>';
    document.getElementById('ws-exec-badge').textContent = 'Ready';
    document.getElementById('ws-exec-badge').className = 'badge badge-gray';
    document.getElementById('ws-exec-time').textContent = '';
  }
}

// ── Project Management & Storage ──────────────────────────────────────────────
async function loadSavedPrograms() {
  const listEl = document.getElementById('ws-programs-list');
  const countEl = document.getElementById('ws-prog-count');
  try {
    savedPrograms = await workspaceApi.listPrograms();
    if (countEl) countEl.textContent = `${savedPrograms.length} items`;
    
    if (savedPrograms.length === 0) {
      listEl.innerHTML = `
        <div style="padding:24px 12px;text-align:center;color:var(--text-muted);font-size:12px">
          No saved projects yet.<br>Click <strong>"Save"</strong> to store your code.
        </div>`;
      return;
    }

    listEl.innerHTML = savedPrograms.map(p => `
      <div class="ws-program-item ${p.id === currentProgramId ? 'active' : ''}" onclick="loadSavedProject(${p.id})" id="ws-prog-${p.id}">
        <div style="display:flex;justify-content:space-between;align-items:flex-start">
          <div style="display:flex;align-items:center;gap:6px">
            <span>${p.language === 'web' ? '🌐' : '🐍'}</span>
            <div style="font-weight:600;font-size:12.5px;color:var(--text-primary);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:130px" title="${p.title}">
              ${p.title}
            </div>
          </div>
          <div style="display:flex;gap:4px;align-items:center;">
            ${p.language === 'web' ? `<button onclick="event.stopPropagation(); loadSavedProject(${p.id}).then(() => openFullscreenApp())" class="btn btn-ghost btn-sm" style="padding:1px 5px;font-size:10px;color:var(--cyan);border:1px solid rgba(6,182,212,0.3);" title="Open in Fullscreen HTML">⛶ Full</button>` : ''}
            <button onclick="event.stopPropagation(); deleteSavedProject(${p.id})" class="ws-del-btn" title="Delete project">✕</button>
          </div>
        </div>
        ${p.description ? `<div style="font-size:11px;color:var(--text-muted);margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${p.description}</div>` : ''}
        <div style="font-size:10px;color:var(--text-muted);margin-top:3px">${formatDateShort(p.updated_at)}</div>
      </div>
    `).join('');
  } catch (err) {
    listEl.innerHTML = `<div style="padding:16px;color:var(--red);font-size:12px">${err.message}</div>`;
  }
}

async function loadSavedProject(id) {
  try {
    const prog = await workspaceApi.getProgram(id);
    currentProgramId = prog.id;
    currentProgramTitle = prog.title;
    
    // Switch language mode
    const mode = prog.language || 'python';
    document.getElementById('ws-lang-select').value = mode;
    
    if (mode === 'web') {
      webFiles.html = prog.code || '';
      if (prog.extra_data) {
        webFiles.css = prog.extra_data.css || '';
        webFiles.js  = prog.extra_data.js || '';
      }
    } else {
      pythonScript = prog.code || '';
    }

    onLanguageModeChange(mode);
    
    document.querySelectorAll('.ws-program-item').forEach(el => el.classList.remove('active'));
    document.getElementById(`ws-prog-${id}`)?.classList.add('active');
    showToast(`Loaded "${prog.title}"`, 'info');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

function loadStarterTemplate(tplId) {
  const tpl = STARTER_TEMPLATES.find(t => t.id === tplId);
  if (!tpl) return;
  currentProgramId = null;
  currentProgramTitle = tpl.title;
  
  document.getElementById('ws-lang-select').value = tpl.language;
  if (tpl.language === 'web') {
    webFiles = { ...tpl.data };
  } else {
    pythonScript = tpl.code;
  }

  onLanguageModeChange(tpl.language);
  showToast(`Loaded "${tpl.title}" template!`, 'info');
}

function newProject(showToastMsg = true) {
  currentProgramId = null;
  const username = getUser()?.username || 'Student';
  currentProgramTitle = `${username}'s Web Project`;
  
  if (currentMode === 'web') {
    webFiles = {
      html: `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${username}'s Web Project</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="card">
    <div class="badge">🌐 Student Studio</div>
    <h1>Hello, ${username}!</h1>
    <p>Welcome to your personal web studio. Edit HTML, CSS, and JS with instant live preview.</p>
    <div style="margin-top:20px;">
      <button class="btn btn-primary" onclick="alert('Hello from ${username}!')">Interactive Button</button>
    </div>
  </div>
  <script src="script.js"></script>
</body>
</html>`,
      css: `* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'Inter', system-ui, sans-serif;
  background: radial-gradient(circle at top, #1e1b4b, #0f172a, #020617);
  color: #f8fafc;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.card {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 20px;
  padding: 40px;
  text-align: center;
  max-width: 440px;
  backdrop-filter: blur(12px);
}
.badge {
  display: inline-block;
  background: rgba(124, 58, 237, 0.25);
  color: #c084fc;
  padding: 4px 14px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 16px;
}
h1 { font-size: 26px; font-weight: 800; margin-bottom: 12px; color: #fff; }
p { color: #94a3b8; font-size: 14px; line-height: 1.6; margin-bottom: 24px; }
.btn-primary {
  padding: 10px 24px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  border: none;
  cursor: pointer;
  background: #7c3aed;
  color: white;
  transition: transform 0.2s;
}
.btn-primary:hover { transform: scale(1.04); }`,
      js: `console.log("Welcome to ${username}'s web studio!");`
    };
    switchWebFileTab('html');
    renderLivePreview();
  } else {
    pythonScript = `# Python Workspace for ${username}\n\ndef main():\n    print("Hello from ${username}!")\n\nif __name__ == "__main__":\n    main()\n`;
    if (editor) editor.setValue(pythonScript);
  }

  document.querySelectorAll('.ws-program-item').forEach(el => el.classList.remove('active'));
  if (showToastMsg) showToast('New project started', 'info');
}

// ── Fullscreen HTML Preview ───────────────────────────────────────────────────
export function openFullscreenApp() {
  saveEditorToMemory();
  const overlay = document.getElementById('ws-fullscreen-overlay');
  const frame = document.getElementById('ws-fullscreen-frame');
  const titleEl = document.getElementById('ws-fs-title');
  if (!overlay || !frame) return;

  if (titleEl) {
    titleEl.textContent = currentProgramTitle || 'Interactive Web Project';
  }

  let htmlContent = webFiles.html || '';
  const cssBlock = `<style>\n${webFiles.css || ''}\n</style>`;
  if (htmlContent.includes('</head>')) {
    htmlContent = htmlContent.replace('</head>', `${cssBlock}\n</head>`);
  } else {
    htmlContent = `${cssBlock}\n${htmlContent}`;
  }

  const jsBlock = `<script>\n${webFiles.js || ''}\n<\/script>`;
  if (htmlContent.includes('</body>')) {
    htmlContent = htmlContent.replace('</body>', `${jsBlock}\n</body>`);
  } else {
    htmlContent = `${htmlContent}\n${jsBlock}`;
  }

  frame.srcdoc = htmlContent;
  overlay.style.display = 'flex';
  overlay.classList.remove('hidden');

  window.addEventListener('keydown', handleFullscreenEsc);
}

export function closeFullscreenApp() {
  const overlay = document.getElementById('ws-fullscreen-overlay');
  if (overlay) {
    overlay.style.display = 'none';
    overlay.classList.add('hidden');
  }
  window.removeEventListener('keydown', handleFullscreenEsc);
}

function handleFullscreenEsc(e) {
  if (e.key === 'Escape') closeFullscreenApp();
}

export function refreshFullscreenApp() {
  openFullscreenApp();
}

export function setFullscreenViewport(width) {
  const frame = document.getElementById('ws-fullscreen-frame');
  if (frame) {
    frame.style.width = width;
    if (width === '100%') {
      frame.style.borderRadius = '0';
      frame.style.height = '100%';
    } else {
      frame.style.borderRadius = '16px';
      frame.style.height = 'calc(100% - 32px)';
    }
  }
}

async function deleteSavedProject(id) {
  if (!confirm('Are you sure you want to delete this project?')) return;
  try {
    await workspaceApi.deleteProgram(id);
    showToast('Project deleted', 'info');
    if (currentProgramId === id) newProject();
    await loadSavedPrograms();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

function switchSidebarTab(tab) {
  document.getElementById('ws-tab-saved').classList.toggle('active', tab === 'saved');
  document.getElementById('ws-tab-templates').classList.toggle('active', tab === 'templates');
  document.getElementById('ws-programs-list').classList.toggle('hidden', tab !== 'saved');
  document.getElementById('ws-templates-list').classList.toggle('hidden', tab !== 'templates');
}

// ── Save Modal ────────────────────────────────────────────────────────────────
function openSaveModal() {
  saveEditorToMemory();
  const modal = document.getElementById('ws-save-modal');
  const titleInput = document.getElementById('ws-modal-title');
  const descInput = document.getElementById('ws-modal-desc');

  if (currentProgramId) {
    const existing = savedPrograms.find(p => p.id === currentProgramId);
    titleInput.value = existing?.title || currentProgramTitle;
    descInput.value = existing?.description || '';
  } else {
    titleInput.value = currentProgramTitle.includes('Untitled') ? '' : currentProgramTitle;
    descInput.value = '';
  }

  modal.classList.remove('hidden');
  titleInput.focus();
}

function closeSaveModal() {
  document.getElementById('ws-save-modal').classList.add('hidden');
}

async function confirmSaveProject() {
  saveEditorToMemory();
  const title = document.getElementById('ws-modal-title').value.trim();
  const description = document.getElementById('ws-modal-desc').value.trim();

  if (!title) {
    showToast('Please enter a project title', 'warn');
    return;
  }

  const btn = document.getElementById('ws-modal-save-btn');
  btn.disabled = true;
  btn.textContent = 'Saving…';

  const payload = {
    title,
    description,
    language: currentMode,
    code: currentMode === 'web' ? webFiles.html : pythonScript,
    extra_data: currentMode === 'web' ? { css: webFiles.css, js: webFiles.js } : null,
  };

  try {
    if (currentProgramId) {
      const updated = await workspaceApi.updateProgram(currentProgramId, payload);
      currentProgramTitle = updated.title;
      showToast('Project updated successfully!', 'success');
    } else {
      const created = await workspaceApi.createProgram(payload);
      currentProgramId = created.id;
      currentProgramTitle = created.title;
      showToast('Project saved to library!', 'success');
    }
    closeSaveModal();
    await loadSavedPrograms();
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Save to Library';
  }
}

// ── Utilities & Export ────────────────────────────────────────────────────────
function copyCurrentCode() {
  saveEditorToMemory();
  const code = currentMode === 'web' ? webFiles[currentWebTab] : pythonScript;
  navigator.clipboard.writeText(code).then(() => {
    showToast('Code copied to clipboard!', 'success');
  });
}

function downloadProjectBundle() {
  saveEditorToMemory();
  if (currentMode === 'web') {
    // Export single full HTML file with embedded CSS and JS
    const bundle = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>${currentProgramTitle}</title>
  <style>
${webFiles.css || ''}
  </style>
</head>
<body>
${webFiles.html || ''}
  <script>
${webFiles.js || ''}
  <\/script>
</body>
</html>`;
    downloadFile(bundle, `${(currentProgramTitle || 'index').toLowerCase().replace(/[^a-z0-9]/g, '_')}.html`, 'text/html');
  } else {
    downloadFile(pythonScript, `${(currentProgramTitle || 'script').toLowerCase().replace(/[^a-z0-9]/g, '_')}.py`, 'text/x-python');
  }
}

function downloadFile(content, filename, type) {
  const blob = new Blob([content], { type: `${type};charset=utf-8` });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast(`Downloaded ${filename}`, 'info');
}

function clearCurrentEditor() {
  if (confirm('Clear the current editor contents?')) {
    if (currentMode === 'web') {
      webFiles[currentWebTab] = '';
    } else {
      pythonScript = '';
    }
    if (editor) editor.setValue('');
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function formatDateShort(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}
