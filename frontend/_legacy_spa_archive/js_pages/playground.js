/**
 * Coding Playground Controller.
 * Free Python experimentation without mandatory test-case evaluation.
 */

import { workspaceApi } from '../api.js';
import { createCodeEditor } from '../components/editor.js';
import { showToast } from '../components/toast.js';

let editor = null;
let savedPrograms = [];

const TEMPLATES = {
  hello: `# Welcome to PyMentor Playground!
# Free experimentation environment — run any standard Python code here.

def greet(name):
    return f"Hello, {name}! Welcome to Python."

print(greet("Explorer"))
print("Calculated squares:", [n**2 for n in range(1, 6)])
`,
  fibonacci: `# Fibonacci Sequence Generator
def fibonacci(n):
    a, b = 0, 1
    seq = []
    for _ in range(n):
        seq.append(a)
        a, b = b, a + b
    return seq

print("First 10 Fibonacci numbers:")
print(fibonacci(10))
`,
  oop: `# Object-Oriented Programming Demo
class Rocket:
    def __init__(self, name, fuel=100):
        self.name = name
        self.fuel = fuel

    def launch(self):
        if self.fuel >= 20:
            self.fuel -= 20
            return f"🚀 {self.name} has launched! Remaining fuel: {self.fuel}%"
        return "⚠️ Insufficient fuel for launch!"

falcon = Rocket("Falcon-9", fuel=50)
print(falcon.launch())
print(falcon.launch())
print(falcon.launch())
`,
  comprehension: `# List and Dictionary Comprehensions
grades = {"Alice": 92, "Bob": 74, "Charlie": 88, "Diana": 95}

# Filter students with grade >= 80
top_students = {name: score for name, score in grades.items() if score >= 80}
print("Top Achievers:", top_students)
`,
  input_demo: `# Interactive User Input Demo
# Provide input in the 'Standard Input' box below before running!
try:
    user_name = input("Enter your name: ")
    user_age = int(input("Enter your age: "))
    print(f"Welcome, {user_name}! In 5 years you will be {user_age + 5}.")
except EOFError:
    print("Notice: No stdin input provided in the box below.")
except Exception as e:
    print(f"Input error: {e}")
`,
};

export async function initPlayground() {
  const mountEl = document.getElementById('pg-editor-mount');
  const templateSelect = document.getElementById('pg-template-select');
  const runBtn = document.getElementById('pg-btn-run');
  const resetBtn = document.getElementById('pg-btn-reset');
  const clearBtn = document.getElementById('pg-btn-clear');
  const saveBtn = document.getElementById('pg-btn-save');
  const libraryBtn = document.getElementById('pg-btn-saved-list');
  const stdinBox = document.getElementById('pg-stdin-input');
  const modalClose = document.getElementById('pg-modal-close');
  const libraryModal = document.getElementById('pg-library-modal');

  // Check if a code snippet was transferred from a lesson
  let starterCode = TEMPLATES.hello;
  const passedCode = sessionStorage.getItem('playground_code');
  if (passedCode) {
    starterCode = passedCode;
    sessionStorage.removeItem('playground_code');
  }

  // Create CodeMirror instance
  editor = createCodeEditor(mountEl, starterCode);

  // Template switch
  templateSelect?.addEventListener('change', (e) => {
    const val = e.target.value;
    if (TEMPLATES[val] && editor) {
      editor.setValue(TEMPLATES[val]);
      if (val === 'input_demo' && stdinBox) {
        stdinBox.value = 'Alice\n20';
      }
    }
  });

  // Run button
  runBtn?.addEventListener('click', runPlaygroundCode);

  // Reset button
  resetBtn?.addEventListener('click', () => {
    const tmplKey = templateSelect?.value || 'hello';
    if (editor) editor.setValue(TEMPLATES[tmplKey] || TEMPLATES.hello);
    showToast('Code reset to starter template.', 'info');
  });

  // Clear output
  clearBtn?.addEventListener('click', () => {
    const consoleOutput = document.getElementById('pg-console-output');
    const statusBadge = document.getElementById('pg-status-badge');
    const execTime = document.getElementById('pg-exec-time');
    if (consoleOutput) consoleOutput.textContent = 'Terminal cleared.';
    if (statusBadge) {
      statusBadge.textContent = 'Idle';
      statusBadge.className = 'badge badge-gray';
    }
    if (execTime) execTime.textContent = '0 ms';
  });

  // Save script
  saveBtn?.addEventListener('click', saveCurrentScript);

  // Library modal
  libraryBtn?.addEventListener('click', () => {
    loadSavedLibrary();
    libraryModal?.classList.remove('hidden');
  });
  modalClose?.addEventListener('click', () => {
    libraryModal?.classList.add('hidden');
  });

  // Load saved programs count
  updateLibraryCount();
}

async function runPlaygroundCode() {
  if (!editor) return;
  const code = editor.getValue();
  const stdinInput = document.getElementById('pg-stdin-input')?.value || '';
  const runBtn = document.getElementById('pg-btn-run');
  const consoleOutput = document.getElementById('pg-console-output');
  const statusBadge = document.getElementById('pg-status-badge');
  const execTime = document.getElementById('pg-exec-time');

  if (runBtn) {
    runBtn.disabled = true;
    runBtn.innerHTML = '<span>Running…</span>';
  }
  if (statusBadge) {
    statusBadge.textContent = 'Running';
    statusBadge.className = 'badge badge-blue';
  }

  try {
    const res = await workspaceApi.runCode(code, stdinInput);

    if (execTime) execTime.textContent = `${res.execution_time_ms || 0} ms`;

    if (res.success) {
      if (statusBadge) {
        statusBadge.textContent = 'Success';
        statusBadge.className = 'badge badge-green';
      }
      if (consoleOutput) {
        consoleOutput.innerHTML = `<span style="color:#4ade80;">${escapeHtml(res.stdout || '(Program executed successfully with no output)')}</span>`;
      }
    } else {
      if (statusBadge) {
        statusBadge.textContent = 'Error';
        statusBadge.className = 'badge badge-red';
      }
      const errText = res.stderr || res.error || 'Execution failed';
      if (consoleOutput) {
        consoleOutput.innerHTML = `<span style="color:#f87171;">${escapeHtml(errText)}</span>`;
      }
    }
  } catch (err) {
    if (statusBadge) {
      statusBadge.textContent = 'Failed';
      statusBadge.className = 'badge badge-red';
    }
    if (consoleOutput) {
      consoleOutput.innerHTML = `<span style="color:#f87171;">Execution error: ${escapeHtml(err.message)}</span>`;
    }
  } finally {
    if (runBtn) {
      runBtn.disabled = false;
      runBtn.innerHTML = '<span>▶ Run Code</span>';
    }
  }
}

async function saveCurrentScript() {
  if (!editor) return;
  const title = prompt('Enter a name for this Python script:', 'My Script');
  if (!title) return;

  const code = editor.getValue();
  try {
    await workspaceApi.createProgram({
      title: title.trim(),
      language: 'python',
      code: code,
      description: 'Saved in Coding Playground',
    });
    showToast(`Saved "${title}" to your library!`, 'success');
    updateLibraryCount();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function updateLibraryCount() {
  const countEl = document.getElementById('pg-saved-count');
  try {
    savedPrograms = await workspaceApi.listPrograms();
    if (countEl) countEl.textContent = savedPrograms.length;
  } catch {
    if (countEl) countEl.textContent = '0';
  }
}

async function loadSavedLibrary() {
  const container = document.getElementById('pg-saved-items-container');
  if (!container) return;
  container.innerHTML = `<div class="flex-center" style="padding:20px;"><div class="loading-spin">⟳</div></div>`;

  try {
    savedPrograms = await workspaceApi.listPrograms();
    if (savedPrograms.length === 0) {
      container.innerHTML = `<div style="text-align:center;padding:24px;color:var(--text-muted);font-size:13px;">No saved scripts yet. Click "Save Script" in the playground to store your experiments!</div>`;
      return;
    }

    container.innerHTML = savedPrograms.map(p => `
      <div style="display:flex;justify-content:space-between;align-items:center;padding:12px 14px;background:rgba(255,255,255,0.02);border:1px solid var(--border);border-radius:8px;margin-bottom:8px;">
        <div>
          <div style="font-size:13.5px;font-weight:700;color:#fff;">${escapeHtml(p.title)}</div>
          <div style="font-size:11px;color:var(--text-muted);">${new Date(p.updated_at).toLocaleDateString()} • Python</div>
        </div>
        <div style="display:flex;gap:8px;">
          <button class="btn btn-primary btn-sm" onclick="window.loadProgramIntoPlayground(${p.id})">Load</button>
          <button class="btn btn-danger btn-sm" onclick="window.deleteProgramFromPlayground(${p.id})">✕</button>
        </div>
      </div>
    `).join('');

    window.loadProgramIntoPlayground = (id) => {
      const prog = savedPrograms.find(p => p.id === id);
      if (prog && editor) {
        editor.setValue(prog.code);
        document.getElementById('pg-library-modal')?.classList.add('hidden');
        showToast(`Loaded "${prog.title}" into editor!`, 'success');
      }
    };

    window.deleteProgramFromPlayground = async (id) => {
      if (!confirm('Are you sure you want to delete this saved script?')) return;
      try {
        await workspaceApi.deleteProgram(id);
        showToast('Script deleted', 'info');
        loadSavedLibrary();
        updateLibraryCount();
      } catch (err) {
        showToast(err.message, 'error');
      }
    };

  } catch (err) {
    container.innerHTML = `<div class="alert alert-error">${err.message}</div>`;
  }
}

function escapeHtml(str) {
  return (str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

