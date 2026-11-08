/**
 * Toast notification component.
 */

export function showToast(message, type = 'info', duration = 3500) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toastEl = document.createElement('div');
  toastEl.className = `toast toast-${type}`;
  toastEl.style.cssText = `
    padding: 12px 18px;
    border-radius: 10px;
    font-size: 13.5px;
    font-weight: 500;
    max-width: 380px;
    backdrop-filter: blur(12px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    opacity: 0;
    transform: translateY(10px);
    transition: all 0.25s ease;
    display: flex;
    align-items: center;
    gap: 10px;
  `;

  const bgStyles = {
    info: 'background: rgba(59, 130, 246, 0.95); color: #fff;',
    success: 'background: rgba(16, 185, 129, 0.95); color: #fff;',
    error: 'background: rgba(239, 68, 68, 0.95); color: #fff;',
    warn: 'background: rgba(245, 158, 11, 0.95); color: #000;',
  };
  toastEl.style.cssText += bgStyles[type] || bgStyles.info;

  const icon = { info: 'ℹ️', success: '✓', error: '⚠️', warn: '⚡' }[type] || 'ℹ️';
  toastEl.innerHTML = `<span style="font-size:16px;">${icon}</span><span>${message}</span>`;

  container.appendChild(toastEl);

  requestAnimationFrame(() => {
    toastEl.style.opacity = '1';
    toastEl.style.transform = 'translateY(0)';
  });

  setTimeout(() => {
    toastEl.style.opacity = '0';
    toastEl.style.transform = 'translateY(10px)';
    setTimeout(() => toastEl.remove(), 250);
  }, duration);
}

export const toast = {
  info: (msg, dur) => showToast(msg, 'info', dur),
  success: (msg, dur) => showToast(msg, 'success', dur),
  error: (msg, dur) => showToast(msg, 'error', dur),
  warn: (msg, dur) => showToast(msg, 'warn', dur),
};
