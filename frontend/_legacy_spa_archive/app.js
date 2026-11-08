/**
 * app.js — SPA router and global state manager.
 * Hash-based routing: #dashboard, #assessment, #learning-path, etc.
 */

import { getToken, setToken, clearToken, getUser, setUser, auth } from './api.js';
import { initAuth } from './auth.js';
import { initDashboard } from './dashboard.js';
import { initAssessment } from './assessment.js';
import { initLearningPath } from './learning-path.js';
import { initMentor } from './mentor.js';
import { initPractice } from './practice.js';
import { initWorkspace } from './workspace.js';
import { initProgress } from './progress.js';
import { initAdmin } from './admin.js';
import { initAdminCreate } from './admin-create.js';

// ── App State ────────────────────────────────────────────────────────────────
export const appState = {
  user: null,
  skillLevel: null,
  currentPage: null,
};

// ── Page Registry ─────────────────────────────────────────────────────────────
const pages = {
  'auth':          { el: '#page-auth',          init: initAuth,         public: true  },
  'dashboard':     { el: '#page-dashboard',      init: initDashboard,    public: false },
  'assessment':    { el: '#page-assessment',     init: initAssessment,   public: false },
  'learning-path': { el: '#page-learning-path',  init: initLearningPath, public: false },
  'mentor':        { el: '#page-mentor',          init: initMentor,       public: false },
  'practice':      { el: '#page-practice',        init: initPractice,     public: false },
  'workspace':     { el: '#page-workspace',       init: initWorkspace,    public: false },
  'progress':      { el: '#page-progress',        init: initProgress,     public: false },
  'admin':         { el: '#page-admin',           init: initAdmin,        public: false },
  'admin-create':  { el: '#page-admin-create',   init: initAdminCreate,  public: false },
};

// ── Navigation ────────────────────────────────────────────────────────────────
export function navigate(page) {
  window.location.hash = `#${page}`;
}
window.navigate = navigate;
window.navigateTo = navigate;

function showPage(pageKey) {
  const config = pages[pageKey];
  if (!config) {
    return navigate(appState.user?.role === 'admin' ? 'admin' : 'dashboard');
  }

  const isAuth = pageKey === 'auth';
  const shell = document.getElementById('app-shell');
  if (shell) {
    shell.classList.toggle('hidden', isAuth);
    shell.style.display = isAuth ? 'none' : 'flex';
  }

  const pageAuth = document.getElementById('page-auth');
  if (pageAuth) {
    pageAuth.classList.toggle('hidden', !isAuth);
  }

  // Hide all pages
  document.querySelectorAll('.page').forEach(el => {
    if (el.id !== 'page-auth' || !isAuth) {
      el.classList.add('hidden');
    }
  });

  const pageEl = document.querySelector(config.el);
  if (pageEl) {
    pageEl.classList.remove('hidden');
    pageEl.classList.add('animate-in');
    setTimeout(() => pageEl.classList.remove('animate-in'), 400);
  }

  // Update sidebar nav
  document.querySelectorAll('.nav-item[data-page]').forEach(el => {
    el.classList.toggle('active', el.dataset.page === pageKey);
  });

  appState.currentPage = pageKey;

  // Update topbar title & role mode badge
  const titles = {
    dashboard:       '🏠 Student Dashboard',
    assessment:      '🎯 Python Diagnostic Assessment',
    'learning-path': '🗺️ Learning Path',
    mentor:          '🤖 AI Mentor',
    practice:        '💻 Coding Practice Lab',
    workspace:       '🌐 Playground & Web Studio',
    progress:        '📊 My Progress',
    admin:           '📊 Platform Analytics & Student Surveillance',
    'admin-create':  '✏️ Curriculum & Content Creator',
  };
  const tb = document.getElementById('topbar-title');
  if (tb) tb.textContent = titles[pageKey] || 'PyMentor';

  const roleModeBadge = document.getElementById('role-mode-badge');
  if (roleModeBadge && appState.user) {
    if (appState.user.role === 'admin') {
      roleModeBadge.textContent = 'Admin Surveillance';
      roleModeBadge.className = 'badge badge-purple';
    } else {
      roleModeBadge.textContent = 'Student Lab';
      roleModeBadge.className = 'badge badge-cyan';
    }
  }

  // Initialise the page
  config.init();
}

async function route() {
  const hash = window.location.hash.slice(1) || 'dashboard';
  const token = getToken();

  if (!token) {
    showPage('auth');
    return;
  }

  // Fetch user info if not cached
  if (!appState.user) {
    try {
      const user = await auth.me();
      appState.user = user;
      setUser(user);
      updateSidebarUser(user);
      updateSidebarNav(user);
    } catch {
      clearToken();
      showPage('auth');
      return;
    }
  }

  const isAdmin = appState.user?.role === 'admin';

  // Strict Role Isolation Route Guard
  if (isAdmin) {
    // Admin only has access to analytics & curriculum creator
    if (hash !== 'admin' && hash !== 'admin-create') {
      showPage('admin');
      return;
    }
  } else {
    // Students can NEVER access admin or admin-create
    if (hash === 'admin' || hash === 'admin-create') {
      showPage('dashboard');
      return;
    }
  }

  const config = pages[hash];
  if (!config || config.public) {
    showPage(isAdmin ? 'admin' : 'dashboard');
    return;
  }

  showPage(hash);
}

// ── Sidebar ───────────────────────────────────────────────────────────────────
function updateSidebarUser(user) {
  const nameEl = document.getElementById('sidebar-username');
  const roleEl = document.getElementById('sidebar-role');
  const avatarEl = document.getElementById('sidebar-avatar');
  if (nameEl)   nameEl.textContent = user.username;
  if (roleEl)   roleEl.textContent = user.role.toUpperCase();
  if (avatarEl) avatarEl.textContent = user.username.charAt(0).toUpperCase();

  // Topbar avatar
  const tbAvatar = document.getElementById('topbar-avatar');
  if (tbAvatar) tbAvatar.textContent = user.username.charAt(0).toUpperCase();
}

function updateSidebarNav(user) {
  const isAdmin = user.role === 'admin';
  const adminNav = document.getElementById('nav-admin-section');
  const studentNav = document.getElementById('nav-student-section');
  if (adminNav) adminNav.classList.toggle('hidden', !isAdmin);
  if (studentNav) studentNav.classList.toggle('hidden', isAdmin);
}

// ── Level Badge ───────────────────────────────────────────────────────────────
export function updateLevelBadge(level) {
  const el = document.getElementById('topbar-level');
  if (!el || !level) return;
  el.textContent = level.charAt(0).toUpperCase() + level.slice(1);
  el.className = `topbar-level-badge level-${level}`;
}

// ── Auth Events ───────────────────────────────────────────────────────────────
export function onLoginSuccess(user) {
  appState.user = user;
  setUser(user);
  updateSidebarUser(user);
  updateSidebarNav(user);
  if (user.role === 'admin') {
    navigate('admin');
  } else {
    navigate('dashboard');
  }
}

export function logout() {
  clearToken();
  appState.user = null;
  appState.skillLevel = null;
  navigate('auth');
  window.location.reload();
}

// ── Toast Notifications ───────────────────────────────────────────────────────
export function showToast(message, type = 'info', duration = 3500) {
  const container = document.getElementById('toast-container') || createToastContainer();
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);
  requestAnimationFrame(() => toast.classList.add('show'));
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

function createToastContainer() {
  const el = document.createElement('div');
  el.id = 'toast-container';
  document.body.appendChild(el);
  return el;
}

// ── Loading Overlay ───────────────────────────────────────────────────────────
export function showLoading(show = true) {
  let overlay = document.getElementById('loading-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.innerHTML = '<div class="loading-spinner"></div>';
    document.body.appendChild(overlay);
  }
  overlay.style.display = show ? 'flex' : 'none';
}

// ── Markdown Renderer ─────────────────────────────────────────────────────────
export function renderMarkdown(text) {
  if (!text) return '';
  if (window.marked) {
    window.marked.setOptions({ breaks: true, gfm: true });
    const html = window.marked.parse(text);
    return html;
  }
  // Fallback: basic formatting
  return text
    .replace(/```python\n?([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>');
}

// ── Format Date ───────────────────────────────────────────────────────────────
export function formatDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

export function formatRelative(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  const now = new Date();
  const diff = Math.floor((now - d) / 1000);
  if (diff < 60)   return 'just now';
  if (diff < 3600) return `${Math.floor(diff/60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff/3600)}h ago`;
  return formatDate(iso);
}

// ── Bootstrap ─────────────────────────────────────────────────────────────────
function init() {
  // Sidebar nav clicks
  document.querySelectorAll('.nav-item[data-page]').forEach(el => {
    el.addEventListener('click', () => navigate(el.dataset.page));
  });

  // Quick Multi-User / Demo Account Switcher
  const switcher = document.getElementById('quick-account-switcher');
  if (switcher) {
    switcher.addEventListener('change', async (e) => {
      const val = e.target.value;
      if (!val) return;
      showToast(`Switching profile to ${val}...`, 'info');
      try {
        const pwd = val === 'admin' ? 'admin123' : 'student123';
        const res = await auth.login(val, pwd);
        setToken(res.access_token);
        const user = await auth.me();
        setUser(user);
        appState.user = user;
        showToast(`Active Account: ${user.username} (${user.role})`, 'success');
        if (user.role === 'admin') {
          navigate('admin');
        } else {
          navigate('dashboard');
        }
        setTimeout(() => window.location.reload(), 250);
      } catch (err) {
        showToast(`Profile switch error: ${err.message}. Please click 'Seed Demo Students' in Admin.`, 'error');
      }
    });
  }

  // Logout button
  document.getElementById('logout-btn')?.addEventListener('click', logout);
  document.getElementById('sidebar-user-card')?.addEventListener('click', () => {
    if (appState.user?.role === 'admin') navigate('admin');
  });

  // Auth expired
  window.addEventListener('auth:expired', () => {
    showToast('Session expired. Please log in again.', 'error');
    showPage('auth');
  });

  // Hash routing
  window.addEventListener('hashchange', route);
  route();
}

if (document.readyState === 'loading') {
  window.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

// Dynamic toast styles
const toastStyle = document.createElement('style');
toastStyle.textContent = `
  #toast-container { position:fixed; bottom:24px; right:24px; z-index:9999; display:flex; flex-direction:column; gap:8px; }
  .toast { padding:12px 18px; border-radius:10px; font-size:14px; font-weight:500; max-width:360px;
    opacity:0; transform:translateY(8px); transition:all 0.3s ease; backdrop-filter:blur(12px); }
  .toast.show { opacity:1; transform:none; }
  .toast-info    { background:rgba(59,130,246,0.9);  color:#fff; }
  .toast-success { background:rgba(16,185,129,0.9);  color:#fff; }
  .toast-error   { background:rgba(239,68,68,0.9);   color:#fff; }
  .toast-warn    { background:rgba(245,158,11,0.9);  color:#000; }
  #loading-overlay { position:fixed; inset:0; background:rgba(7,7,15,0.7); display:flex;
    align-items:center; justify-content:center; z-index:9998; backdrop-filter:blur(4px); }
  .loading-spinner { width:44px; height:44px; border:3px solid rgba(124,58,237,0.2);
    border-top-color:#7c3aed; border-radius:50%; animation:spin 0.8s linear infinite; }
`;
document.head.appendChild(toastStyle);
