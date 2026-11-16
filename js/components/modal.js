/**
 * modal.js
 * Professional in-website modal dialogs (Prompt, Confirm, Alert)
 * Matches PyMentor Warm Champagne luxury aesthetic — no native browser popups!
 */

export function showPromptModal({
  title = 'Input Required',
  message = 'Please enter a value:',
  placeholder = '',
  defaultValue = '',
  confirmText = 'Save',
  cancelText = 'Cancel',
} = {}) {
  return new Promise((resolve) => {
    // Remove any existing dialog
    document.querySelectorAll('.custom-inpage-modal-overlay').forEach(el => el.remove());

    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay custom-inpage-modal-overlay';
    overlay.style.cssText = `
      position: fixed; inset: 0; background: rgba(44, 26, 14, 0.55);
      backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);
      z-index: 99999; display: flex; align-items: center; justify-content: center;
      padding: 20px; animation: modalFadeIn 0.2s ease-out;
    `;

    overlay.innerHTML = `
      <div class="modal-content-card" style="
        background: #FFFFFF;
        border: 1.5px solid rgba(200, 160, 100, 0.3);
        border-radius: 16px;
        width: 100%;
        max-width: 440px;
        box-shadow: 0 20px 60px rgba(44, 26, 14, 0.25);
        overflow: hidden;
        animation: modalScaleUp 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
      ">
        <div style="
          padding: 18px 24px;
          border-bottom: 1px solid rgba(200, 160, 100, 0.18);
          display: flex; align-items: center; justify-content: space-between;
          background: #FFFDF9;
        ">
          <h3 style="font-size: 16px; font-weight: 800; color: #1C0E04; margin: 0; display:flex; align-items:center; gap:8px;">
            <span>💾</span> ${title}
          </h3>
          <button id="custom-modal-close" style="
            background: transparent; border: none; font-size: 18px; color: #A07050;
            cursor: pointer; padding: 4px 8px; border-radius: 6px; line-height: 1;
          ">✕</button>
        </div>

        <form id="custom-modal-form" style="padding: 24px; display: flex; flex-direction: column; gap: 16px;">
          <label style="font-size: 13.5px; font-weight: 600; color: #3D2110; line-height: 1.5;">
            ${message}
          </label>
          <input type="text" id="custom-modal-input" value="${defaultValue}" placeholder="${placeholder}" style="
            padding: 10px 14px; border-radius: 10px;
            border: 1.5px solid #E8D5B8; background: #FFFDF9;
            color: #1C0E04; font-size: 14px; outline: none; width: 100%;
            transition: all 0.2s; box-sizing: border-box;
          " required />

          <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 6px;">
            <button type="button" id="custom-modal-cancel" style="
              padding: 9px 18px; border-radius: 10px; border: 1.5px solid #E8D5B8;
              background: #FFFFFF; color: #6B4226; font-size: 13px; font-weight: 600;
              cursor: pointer; transition: all 0.18s;
            ">${cancelText}</button>
            <button type="submit" id="custom-modal-confirm" style="
              padding: 9px 22px; border-radius: 10px; border: none;
              background: linear-gradient(135deg, #F59E0B, #D97706);
              color: #FFFFFF; font-size: 13px; font-weight: 700;
              cursor: pointer; box-shadow: 0 4px 14px rgba(217, 119, 6, 0.35);
              transition: all 0.18s;
            ">${confirmText}</button>
          </div>
        </form>
      </div>
    `;

    document.body.appendChild(overlay);

    const input = overlay.querySelector('#custom-modal-input');
    const closeBtn = overlay.querySelector('#custom-modal-close');
    const cancelBtn = overlay.querySelector('#custom-modal-cancel');
    const form = overlay.querySelector('#custom-modal-form');

    input.focus();
    input.select();

    const cleanup = (val) => {
      overlay.remove();
      resolve(val);
    };

    closeBtn.addEventListener('click', () => cleanup(null));
    cancelBtn.addEventListener('click', () => cleanup(null));

    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) cleanup(null);
    });

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      cleanup(input.value);
    });

    document.addEventListener('keydown', function escHandler(e) {
      if (e.key === 'Escape') {
        document.removeEventListener('keydown', escHandler);
        cleanup(null);
      }
    });
  });
}

export function showConfirmModal({
  title = 'Confirmation',
  message = 'Are you sure you want to proceed?',
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  isDanger = false,
} = {}) {
  return new Promise((resolve) => {
    document.querySelectorAll('.custom-inpage-modal-overlay').forEach(el => el.remove());

    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay custom-inpage-modal-overlay';
    overlay.style.cssText = `
      position: fixed; inset: 0; background: rgba(44, 26, 14, 0.55);
      backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);
      z-index: 99999; display: flex; align-items: center; justify-content: center;
      padding: 20px;
    `;

    overlay.innerHTML = `
      <div class="modal-content-card" style="
        background: #FFFFFF;
        border: 1.5px solid rgba(200, 160, 100, 0.3);
        border-radius: 16px;
        width: 100%; max-width: 420px;
        box-shadow: 0 20px 60px rgba(44, 26, 14, 0.25);
        overflow: hidden;
      ">
        <div style="padding: 22px 24px 12px;">
          <h3 style="font-size: 16px; font-weight: 800; color: #1C0E04; margin-bottom: 8px;">
            ${isDanger ? '⚠️ ' : ''}${title}
          </h3>
          <p style="font-size: 13.5px; color: #6B4226; line-height: 1.5; margin: 0;">
            ${message}
          </p>
        </div>
        <div style="padding: 16px 24px; background:#FFFDF9; border-top:1px solid rgba(200, 160, 100, 0.15); display: flex; justify-content: flex-end; gap: 10px;">
          <button id="custom-confirm-cancel" style="
            padding: 8px 18px; border-radius: 10px; border: 1.5px solid #E8D5B8;
            background: #FFFFFF; color: #6B4226; font-size: 13px; font-weight: 600; cursor: pointer;
          ">${cancelText}</button>
          <button id="custom-confirm-ok" style="
            padding: 8px 22px; border-radius: 10px; border: none;
            background: ${isDanger ? 'linear-gradient(135deg, #EF4444, #DC2626)' : 'linear-gradient(135deg, #F59E0B, #D97706)'};
            color: #FFFFFF; font-size: 13px; font-weight: 700; cursor: pointer;
            box-shadow: 0 4px 14px ${isDanger ? 'rgba(239, 68, 68, 0.35)' : 'rgba(217, 119, 6, 0.35)'};
          ">${confirmText}</button>
        </div>
      </div>
    `;

    document.body.appendChild(overlay);

    const okBtn = overlay.querySelector('#custom-confirm-ok');
    const cancelBtn = overlay.querySelector('#custom-confirm-cancel');

    const cleanup = (res) => {
      overlay.remove();
      resolve(res);
    };

    okBtn.addEventListener('click', () => cleanup(true));
    cancelBtn.addEventListener('click', () => cleanup(false));
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) cleanup(false);
    });
  });
}

