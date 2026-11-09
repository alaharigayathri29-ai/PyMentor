/**
 * auth.js
 * Multi-Page Authentication Handler (Login, Register, Logout)
 */

import { authApi, setToken, setUser, clearToken, getToken } from './api.js?v=20261108_v17';
import { showToast } from './components/toast.js?v=20261108_v17';

export function initLogin() {
  const urlParams = new URLSearchParams(window.location.search);
  const isSwitching = urlParams.get('switch') === 'true' || urlParams.get('logout') === 'true';

  if (isSwitching) {
    clearToken();
  } else if (getToken()) {
    // If already logged in and not explicitly switching accounts, redirect
    authApi.me().then(user => {
      setUser(user);
      const dest = sessionStorage.getItem('redirectAfterLogin') || (user.role === 'admin' ? '/admin/dashboard.html' : '/dashboard.html');
      sessionStorage.removeItem('redirectAfterLogin');
      window.location.replace(dest);
    }).catch(() => {
      clearToken();
    });
  }

  // Bind One-Click Quick Demo Student Login buttons
  document.querySelectorAll('.quick-login-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const u = btn.dataset.user;
      const p = btn.dataset.pwd;
      const usernameInput = document.getElementById('login-username');
      const passwordInput = document.getElementById('login-password');
      if (usernameInput) usernameInput.value = u;
      if (passwordInput) passwordInput.value = p;

      clearToken();
      btn.style.opacity = '0.6';
      btn.style.pointerEvents = 'none';

      try {
        const res = await authApi.login(u, p);
        setToken(res.access_token);
        const user = await authApi.me();
        setUser(user);
        showToast(`Signed in as ${user.username}!`, 'success');
        const dest = user.role === 'admin' ? '/admin/dashboard.html' : '/dashboard.html';
        setTimeout(() => window.location.replace(dest), 200);
      } catch (err) {
        showToast(`Quick login failed: ${err.message}`, 'error');
        btn.style.opacity = '1';
        btn.style.pointerEvents = 'auto';
      }
    });
  });

  const form = document.getElementById('login-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const usernameInput = document.getElementById('login-username');
    const passwordInput = document.getElementById('login-password');
    const btn = document.getElementById('login-submit-btn') || document.getElementById('login-btn');
    const alertBox = document.getElementById('auth-alert');

    const username = usernameInput?.value.trim();
    const password = passwordInput?.value;

    if (!username || !password) return;

    if (alertBox) alertBox.innerHTML = '';
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<span>Signing in…</span>';
    }

    try {
      const res = await authApi.login(username, password);
      setToken(res.access_token);
      const user = await authApi.me();
      setUser(user);

      showToast(`Welcome back, ${user.username}!`, 'success');

      const dest = sessionStorage.getItem('redirectAfterLogin') || (user.role === 'admin' ? '/admin/dashboard.html' : '/dashboard.html');
      sessionStorage.removeItem('redirectAfterLogin');

      setTimeout(() => {
        window.location.replace(dest);
      }, 300);
    } catch (err) {
      if (alertBox) {
        alertBox.innerHTML = `<div class="alert alert-error">⚠️ ${err.message}</div>`;
      }
      showToast(err.message, 'error');
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<span>Sign In →</span>';
      }
    }
  });
}

export function initRegister() {
  const form = document.getElementById('register-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('reg-username')?.value.trim();
    const email = document.getElementById('reg-email')?.value.trim();
    const password = document.getElementById('reg-password')?.value;
    const btn = document.getElementById('reg-submit-btn') || document.getElementById('register-btn');
    const alertBox = document.getElementById('auth-alert');

    if (password && password.length < 6) {
      if (alertBox) {
        alertBox.innerHTML = '<div class="alert alert-error">Password must be at least 6 characters</div>';
      }
      return;
    }

    if (alertBox) alertBox.innerHTML = '';
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<span>Creating account…</span>';
    }

    try {
      await authApi.register({ username, email, password });
      showToast('Account created successfully! Signing you in…', 'success');
      
      // Auto-login newly registered user
      try {
        const loginRes = await authApi.login(username, password);
        setToken(loginRes.access_token);
        const me = await authApi.me();
        setUser(me);
        setTimeout(() => {
          window.location.replace('/assessment.html');
        }, 500);
      } catch {
        setTimeout(() => {
          window.location.replace('/login.html');
        }, 800);
      }
    } catch (err) {
      if (alertBox) {
        alertBox.innerHTML = `<div class="alert alert-error">⚠️ ${err.message}</div>`;
      }
      showToast(err.message, 'error');
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<span>Create Account →</span>';
      }
    }
  });
}

export function logout() {
  clearToken();
  showToast('You have been signed out.', 'info');
  window.location.replace('/login.html');
}

// Auto-initialize on page load
if (typeof document !== 'undefined') {
  if (document.getElementById('login-form')) {
    initLogin();
  }
  if (document.getElementById('register-form')) {
    initRegister();
  }
}
