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

    const displayName = (user.username === 'honey_qis')
      ? 'A.sri Lakshmi Gayatri'
      : (user.username || 'Student');

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
  document.querySelectorAll('.sidebar-nav a.nav-item').forEach(link => {
    const pageAttr = link.getAttribute('data-page');
    const href = link.getAttribute('href') || '';
    if (pageAttr === activePageKey || href.includes(activePageKey + '.html')) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });

  // Attach logout handler
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn && !logoutBtn.dataset.bound) {
    logoutBtn.dataset.bound = 'true';
    logoutBtn.addEventListener('click', (e) => {
      e.preventDefault();
      clearToken();
      window.location.replace('/login.html');
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

