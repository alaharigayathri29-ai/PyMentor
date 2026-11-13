/**
 * common.js
 * Shared utilities for Multi-Page Application:
 * - Authentication verification & role checking on every page
 * - Unified sidebar, topbar, and user profile state
 * - Logout handler
 * - Empty state renderer
 */

import { getToken, clearToken, setUser, getUser, authApi } from './api.js?v=20261108_v17';
import { showToast } from './components/toast.js?v=20261108_v17';

/**
 * Checks authentication for the current page.
 * If user is not authenticated, redirects to /login.html.
 * If requireAdmin is true and user is not an admin, redirects to /dashboard.html.
 */
export async function requireAuth(options = { requireAdmin: false }) {
  const token = getToken();
  if (!token) {
    sessionStorage.setItem('redirectAfterLogin', window.location.pathname + window.location.search);
    window.location.replace('/login.html');
    return null;
  }

  try {
    const user = await authApi.me();
    setUser(user);

    if (options.requireAdmin && user.role !== 'admin') {
      showToast('Access restricted: Administrator role required', 'error');
      window.location.replace('/dashboard.html');
      return null;
    }

    return user;
  } catch (err) {
    clearToken();
    sessionStorage.setItem('redirectAfterLogin', window.location.pathname + window.location.search);
    window.location.replace('/login.html');
    return null;
  }
}

/**
 * Sets up the standard multi-page layout: sidebar, topbar, user card, and active link.
 */
export function initLayout(activePageKey, user) {
  if (!user) {
    user = getUser();
  }

  // Populate user display in sidebar
  if (user) {
    const initial = (user.username || 'U')[0].toUpperCase();
    const usernameEl = document.getElementById('sidebar-username');
    const roleEl = document.getElementById('sidebar-role');
    const avatarEl = document.getElementById('sidebar-avatar');
    const topAvatar = document.getElementById('topbar-avatar');
    const roleBadge = document.getElementById('role-mode-badge');
    const adminNav = document.getElementById('nav-admin-section');

    const studentNameMap = {
      'honey_qis': 'A.sri Lakshmi Gayatri',
      'priya_beginner': 'Priya Sharma (Beginner)',
      'rahul_intermediate': 'Rahul Verma (Interm.)',
      'ananya_advanced': 'Ananya Iyer (Advanced)',
      'vikram_code': 'Vikram Patel',
      'admin': 'Administrator',
    };
    const displayName = studentNameMap[user.username] || (user.username || 'Student');

    if (usernameEl) usernameEl.textContent = displayName;
    if (roleEl) roleEl.textContent = user.role === 'admin' ? 'Administrator' : 'STUDENT · QISCET';
    if (avatarEl) avatarEl.textContent = displayName[0].toUpperCase();

    const topName = document.getElementById('topbar-username');
    if (topName) topName.textContent = displayName;
    if (topAvatar) topAvatar.textContent = displayName[0].toUpperCase();

    const topPill = document.getElementById('topbar-user-pill');
    if (topPill && !topPill.dataset.profileBound) {
      topPill.dataset.profileBound = 'true';
      topPill.style.cursor = 'pointer';
      topPill.addEventListener('click', () => { window.location.href = '/profile.html'; });
    }

    if (topAvatar) {
      topAvatar.textContent = initial;
      topAvatar.title = 'View Student Profile';
      topAvatar.style.cursor = 'pointer';
      if (!topAvatar.dataset.profileBound) {
        topAvatar.dataset.profileBound = 'true';
        topAvatar.addEventListener('click', () => { window.location.href = '/profile.html'; });
      }
    }

    const userCard = document.getElementById('sidebar-user-card');
    if (userCard && !userCard.dataset.profileBound) {
      userCard.dataset.profileBound = 'true';
      userCard.title = 'View Student Profile';
      userCard.style.cursor = 'pointer';
      userCard.addEventListener('click', () => { window.location.href = '/profile.html'; });
    }

    if (roleBadge) {
      if (user.role === 'admin') {
        roleBadge.textContent = 'Administrator';
        roleBadge.className = 'badge badge-purple';
      } else {
        roleBadge.textContent = 'Student Portal';
        roleBadge.className = 'badge badge-blue';
      }
    }

    // Toggle admin nav section visibility based on role
    if (adminNav) {
      if (user.role === 'admin') {
        adminNav.classList.remove('hidden');
      } else {
        adminNav.classList.add('hidden');
      }
    }
  }

  // Highlight the active sidebar item
  const currentSearch = window.location.search;
  document.querySelectorAll('.sidebar-nav a.nav-item').forEach(link => {
    const pageAttr = link.getAttribute('data-page');
    const href = link.getAttribute('href') || '';
    
    let isMatch = false;
    if (pageAttr && pageAttr.startsWith('course-')) {
      const courseName = pageAttr.replace('course-', '');
      isMatch = currentSearch.includes(`course=${courseName}`) || (pageAttr === 'course-python' && !currentSearch.includes('course=') && window.location.pathname.includes('learning-path'));
    } else {
      isMatch = pageAttr === activePageKey || (href.includes(activePageKey + '.html') && !href.includes('course='));
    }

    if (isMatch) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }

    // Auto-close sidebar on mobile or when switching module/course
    link.addEventListener('click', () => {
      const sidebar = document.getElementById('sidebar');
      const backdrop = document.getElementById('sidebar-backdrop');
      if (window.innerWidth <= 768 && sidebar) {
        sidebar.classList.remove('open');
        if (backdrop) backdrop.classList.remove('active');
      }
    });
  });

  // Setup Sidebar Toggle and Responsive Backdrop
  setupSidebarControls();

  // Attach logout handler
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn && !logoutBtn.dataset.bound) {
    logoutBtn.dataset.bound = 'true';
    logoutBtn.addEventListener('click', (e) => {
      e.preventDefault();
      clearToken();
      window.location.replace('/login.html?switch=true');
    });
  }

  // Handle session expiration
  window.addEventListener('auth:expired', () => {
    window.location.replace('/login.html');
  });
}

/**
 * Helper to render a professional empty state into any container element.
 * Complies with requirement 6 (Empty states instead of fake data).
 */
export function renderEmptyState(container, { icon = '📭', title = 'No data available', message = '', actionText = '', actionHref = '' }) {
  if (!container) return;
  container.innerHTML = `
    <div class="empty-state-card" style="padding:48px 24px;text-align:center;background:#F8FAFC;border:1.5px dashed var(--border);border-radius:var(--r-xl);margin:16px 0;">
      <div style="font-size:42px;margin-bottom:12px;">${icon}</div>
      <h3 style="font-size:17px;font-weight:700;color:var(--text-primary);margin-bottom:6px;">${escapeHtml(title)}</h3>
      <p style="font-size:13.5px;color:var(--text-secondary);max-width:440px;margin:0 auto 18px;line-height:1.5;">${escapeHtml(message)}</p>
      ${actionText && actionHref ? `
        <a href="${actionHref}" class="btn btn-primary btn-sm" style="display:inline-flex;align-items:center;gap:6px;text-decoration:none;">
          <span>${escapeHtml(actionText)}</span> →
        </a>
      ` : ''}
    </div>
  `;
}

export function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * Responsive Sidebar Toggle and Backdrop for Mobile & Desktop
 */
function setupSidebarControls() {
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;

  // 1. Create or get backdrop
  let backdrop = document.getElementById('sidebar-backdrop');
  if (!backdrop) {
    backdrop = document.createElement('div');
    backdrop.id = 'sidebar-backdrop';
    backdrop.className = 'sidebar-backdrop';
    document.body.appendChild(backdrop);
  }

  backdrop.onclick = () => {
    sidebar.classList.remove('open');
    sidebar.classList.add('collapsed');
    backdrop.classList.remove('active');
  };

  // 2. Inject toggle button in topbar if not already present
  const topbarLeft = document.querySelector('.topbar-left');
  if (topbarLeft && !document.getElementById('sidebar-toggle-btn')) {
    const toggleBtn = document.createElement('button');
    toggleBtn.id = 'sidebar-toggle-btn';
    toggleBtn.className = 'topbar-icon-btn';
    toggleBtn.setAttribute('title', 'Toggle Navigation Menu');
    toggleBtn.innerHTML = '☰';
    toggleBtn.style.cssText = `
      margin-right: 8px; font-size: 16px; font-weight: bold;
      border-radius: 8px; display: inline-flex; align-items: center; justify-content: center;
      cursor: pointer; transition: all 0.2s;
    `;
    toggleBtn.onclick = () => {
      if (window.innerWidth <= 768) {
        sidebar.classList.toggle('open');
        backdrop.classList.toggle('active', sidebar.classList.contains('open'));
      } else {
        sidebar.classList.toggle('collapsed');
      }
    };
    topbarLeft.insertBefore(toggleBtn, topbarLeft.firstChild);
  }
}

