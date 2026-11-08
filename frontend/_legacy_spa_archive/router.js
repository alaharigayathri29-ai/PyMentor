/**
 * router.js
 * Client-Side Router with Dynamic HTML Template Loading & Strict Role Guards.
 */

import { getToken, getUser, setUser, clearToken, authApi } from './api.js';
import { initLogin, initRegister, logout } from './auth.js';
import { showToast } from './components/toast.js';

// Page Controllers
import { initDashboard } from './pages/dashboard.js';
import { initAssessment } from './pages/assessment.js';
import { initLearningPath } from './pages/learning-path.js';
import { initLesson } from './pages/lesson.js';
import { initPractice } from './pages/practice.js';
import { initPlayground } from './pages/playground.js';
import { initMentor } from './pages/mentor.js';
import { initProgress } from './pages/progress.js';
import { initAdminDashboard } from './pages/admin-dashboard.js';
import { initAdminStudents } from './pages/admin-students.js';
import { initAdminTopics } from './pages/admin-topics.js';
import { initAdminAnalytics } from './pages/admin-analytics.js';

const ROUTES = {
  // Public Auth
  'login': { template: 'pages/login.html', init: initLogin, title: 'Sign In', public: true },
  'register': { template: 'pages/register.html', init: initRegister, title: 'Create Account', public: true },

  // Student Learning Portal
  'dashboard': { template: 'pages/dashboard.html', init: initDashboard, title: 'Student Dashboard', role: 'student' },
  'assessment': { template: 'pages/assessment.html', init: initAssessment, title: 'Skill Assessment', role: 'student' },
  'learning-path': { template: 'pages/learning-path.html', init: initLearningPath, title: 'Curriculum Map', role: 'student' },
  'lesson': { template: 'pages/lesson.html', init: initLesson, title: 'Interactive Lesson', role: 'student' },
  'practice': { template: 'pages/practice.html', init: initPractice, title: 'Code Practice Lab', role: 'student' },
  'playground': { template: 'pages/playground.html', init: initPlayground, title: 'Coding Playground', role: 'student' },
  'mentor': { template: 'pages/mentor.html', init: initMentor, title: 'AI Mentor', role: 'student' },
  'progress': { template: 'pages/progress.html', init: initProgress, title: 'My Progress', role: 'student' },

  // Admin Management Portal
  'admin-dashboard': { template: 'pages/admin/dashboard.html', init: initAdminDashboard, title: 'Admin Overview', role: 'admin' },
  'admin-students': { template: 'pages/admin/students.html', init: initAdminStudents, title: 'Student Directory', role: 'admin' },
  'admin-topics': { template: 'pages/admin/topics.html', init: initAdminTopics, title: 'Curriculum & Content Creator', role: 'admin' },
  'admin-analytics': { template: 'pages/admin/analytics.html', init: initAdminAnalytics, title: 'Platform Analytics', role: 'admin' },
};

const templateCache = new Map();

async function handleRoute() {
  const hash = window.location.hash.slice(1);
  const routeName = (hash.split('?')[0] || '').trim();
  const token = getToken();
  let user = getUser();

  // Validate or sync active user profile from token
  if (token && (!user || !user.role)) {
    try {
      user = await authApi.me();
      setUser(user);
    } catch (e) {
      clearToken();
      user = null;
    }
  }

  // Not authenticated
  if (!token || !user) {
    if (routeName !== 'login' && routeName !== 'register') {
      window.location.hash = '#login';
      return;
    }
  }

  // Authenticated user landing on empty or auth page -> redirect to landing
  if (token && user && (routeName === 'login' || routeName === 'register' || !routeName)) {
    if (user.role === 'admin') {
      window.location.hash = '#admin-dashboard';
    } else {
      window.location.hash = '#dashboard';
    }
    return;
  }

  const targetRoute = routeName || (user?.role === 'admin' ? 'admin-dashboard' : 'dashboard');
  const routeConfig = ROUTES[targetRoute];

  if (!routeConfig) {
    // Route not found
    window.location.hash = user?.role === 'admin' ? '#admin-dashboard' : '#dashboard';
    return;
  }

  // Role Protection: Prevent non-admin access to admin routes
  if (routeConfig.role === 'admin' && user?.role !== 'admin') {
    showToast('Access restricted: Administrator role required', 'error');
    window.location.hash = '#dashboard';
    return;
  }

  await loadPage(targetRoute, routeConfig, user);
}

async function loadPage(routeName, config, user) {
  const shell = document.getElementById('app-shell');
  const sidebar = document.getElementById('sidebar');
  const topbar = document.querySelector('.topbar');
  const mainContent = document.getElementById('main-content');
  const topbarTitle = document.getElementById('topbar-title');
  const roleModeBadge = document.getElementById('role-mode-badge');
  const levelBadge = document.getElementById('topbar-level-badge');
  const topbarAvatar = document.getElementById('topbar-avatar');
  const sidebarAvatar = document.getElementById('sidebar-avatar');
  const sidebarUsername = document.getElementById('sidebar-username');
  const sidebarRole = document.getElementById('sidebar-role');
  const adminSection = document.getElementById('nav-admin-section');

  shell?.classList.remove('hidden');

  if (config.public) {
    if (sidebar) sidebar.style.display = 'none';
    if (topbar) topbar.style.display = 'none';
  } else {
    if (sidebar) sidebar.style.display = 'flex';
    if (topbar) topbar.style.display = 'flex';

    if (topbarTitle) topbarTitle.textContent = config.title;

    if (user) {
      const initial = (user.username || 'U')[0].toUpperCase();
      if (sidebarUsername) sidebarUsername.textContent = user.username;
      if (sidebarRole) sidebarRole.textContent = user.role;
      if (sidebarAvatar) sidebarAvatar.textContent = initial;
      if (topbarAvatar) topbarAvatar.textContent = initial;

      if (user.role === 'admin') {
        if (adminSection) adminSection.classList.remove('hidden');
        if (roleModeBadge) {
          roleModeBadge.textContent = 'Administrator';
          roleModeBadge.className = 'badge badge-purple';
        }
        if (levelBadge) {
          levelBadge.textContent = 'Admin Console';
          levelBadge.className = 'badge badge-purple';
        }
      } else {
        if (adminSection) adminSection.classList.add('hidden');
        if (roleModeBadge) {
          roleModeBadge.textContent = 'Student Portal';
          roleModeBadge.className = 'badge badge-blue';
        }
        if (levelBadge) {
          levelBadge.textContent = 'Python Learner';
          levelBadge.className = 'badge badge-beginner';
        }
      }
    }

    // Active state on sidebar nav
    document.querySelectorAll('.sidebar-nav .nav-item').forEach(el => {
      if (el.getAttribute('data-page') === routeName) {
        el.classList.add('active');
      } else {
        el.classList.remove('active');
      }
    });
  }

  // Load HTML template
  let html = templateCache.get(config.template);
  if (!html) {
    try {
      const res = await fetch(config.template);
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      html = await res.text();
      templateCache.set(config.template, html);
    } catch (err) {
      if (mainContent) {
        mainContent.innerHTML = `<div style="padding:40px;color:var(--red);text-align:center;">Failed to load view: ${err.message}</div>`;
      }
      return;
    }
  }

  if (mainContent) {
    mainContent.innerHTML = html;
  }

  // Run controller initializer
  if (typeof config.init === 'function') {
    try {
      await config.init();
    } catch (err) {
      console.error(`Error initializing view '${routeName}':`, err);
    }
  }
}

// Global Nav & Event Bindings
function initApp() {
  document.querySelectorAll('.sidebar-nav .nav-item').forEach(item => {
    item.addEventListener('click', () => {
      const page = item.getAttribute('data-page');
      if (page) {
        window.location.hash = '#' + page;
      }
    });
  });

  document.getElementById('logout-btn')?.addEventListener('click', () => {
    logout();
  });

  window.addEventListener('hashchange', handleRoute);
  handleRoute();
}

// Start application on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}

