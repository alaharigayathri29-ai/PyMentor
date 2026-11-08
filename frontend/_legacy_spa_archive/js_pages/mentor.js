/**
 * AI Mentor Chat Controller.
 * Interactive AI pedagogy with collapsible history, action chips, and code copy tools.
 */

import { mentorApi } from '../api.js';
import { renderMarkdown } from '../utils/markdown.js';
import { showToast } from '../components/toast.js';
import { formatRelative } from '../utils/formatters.js';

let sessions = [];
let activeSessionId = null;
let isSending = false;

export async function initMentor() {
  const sidebar = document.getElementById('mentor-sidebar');
  const toggleBtn = document.getElementById('btn-toggle-sidebar');
  const newBtn = document.getElementById('btn-mentor-new');
  const deleteBtn = document.getElementById('btn-delete-session');
  const sendBtn = document.getElementById('btn-chat-send');
  const textarea = document.getElementById('chat-user-input');
  const chips = document.querySelectorAll('.action-chip');
  const modeIndicator = document.getElementById('chat-mode-indicator');

  // Check AI Provider mode
  try {
    const st = await mentorApi.status();
    if (modeIndicator) {
      modeIndicator.textContent = st.is_mock
        ? 'Offline Educational Model'
        : `Connected to ${st.model || 'OpenAI'}`;
    }
  } catch {}

  // Sidebar toggle
  toggleBtn?.addEventListener('click', () => {
    sidebar?.classList.toggle('collapsed');
  });

  // New Chat
  newBtn?.addEventListener('click', async () => {
    try {
      const newSess = await mentorApi.newSession('Python Inquiry');
      showToast('Created new conversation.', 'success');
      await loadSessions(newSess.id);
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // Delete Chat
  deleteBtn?.addEventListener('click', async () => {
    if (!activeSessionId) return;
    if (!confirm('Are you sure you want to delete this conversation?')) return;
    try {
      await mentorApi.deleteSession(activeSessionId);
      showToast('Conversation deleted.', 'info');
      activeSessionId = null;
      await loadSessions();
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // Action chips
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      const action = chip.dataset.action;
      const prompts = {
        explain_differently: 'Can you please explain this concept differently using a new analogy or visualization?',
        hint: 'Can you give me a small hint to point me in the right direction without giving away the full answer?',
        practice_problem: 'Can you generate an engaging practice coding challenge on this topic for my skill level?',
        explain_error: 'Can you help me analyze why this code or logic error might occur and how to debug it?',
        continue_learning: 'What is the logical next step or concept I should study after mastering this topic?',
      };
      const text = prompts[action] || 'Help me learn Python.';
      if (textarea) textarea.value = text;
      handleSendMessage(action);
    });
  });

  // Send message
  sendBtn?.addEventListener('click', () => handleSendMessage());
  textarea?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  });

  // Load conversations
  await loadSessions();
}

async function loadSessions(selectId = null) {
  const container = document.getElementById('mentor-sessions-container');
  if (!container) return;
  container.innerHTML = `<div class="flex-center" style="padding:20px;"><div class="loading-spin">⟳</div></div>`;

  try {
    sessions = await mentorApi.sessions();

    if (!sessions || sessions.length === 0) {
      // Auto-create initial session if none exist
      const first = await mentorApi.newSession('Welcome & Python Basics');
      sessions = [first];
    }

    container.innerHTML = sessions.map(s => `
      <div class="session-item ${s.id === (selectId || activeSessionId || sessions[0].id) ? 'active' : ''}" onclick="window.selectMentorSession(${s.id})">
        <div style="min-width:0;flex:1;">
          <div style="font-weight:600;font-size:13px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#fff;">
            ${escapeHtml(s.title || 'New Session')}
          </div>
          <div style="font-size:11px;color:var(--text-muted);">${formatRelative(s.created_at)}</div>
        </div>
      </div>
    `).join('');

    const targetId = selectId || activeSessionId || sessions[0].id;
    await openSession(targetId);

    window.selectMentorSession = (id) => {
      document.querySelectorAll('.session-item').forEach(item => item.classList.remove('active'));
      openSession(id);
    };

  } catch (err) {
    container.innerHTML = `<div class="alert alert-error">${err.message}</div>`;
  }
}

async function openSession(sessionId) {
  activeSessionId = sessionId;
  const messagesBox = document.getElementById('chat-messages-box');
  const sessionTitle = document.getElementById('chat-session-title');
  if (!messagesBox) return;

  const currentSess = sessions.find(s => s.id === sessionId);
  if (sessionTitle && currentSess) {
    sessionTitle.textContent = currentSess.title || 'PyMentor Assistant';
  }

  messagesBox.innerHTML = `<div class="flex-center" style="height:200px;"><div class="loading-spin">⟳</div></div>`;

  try {
    const msgs = await mentorApi.messages(sessionId);
    if (!msgs || msgs.length === 0) {
      messagesBox.innerHTML = `
        <div style="text-align:center;padding:48px 20px;color:var(--text-muted);">
          <div style="font-size:48px;margin-bottom:12px;">💬</div>
          <h3 style="font-size:16px;color:#fff;margin-bottom:6px;">How can I help you today?</h3>
          <p style="font-size:13px;max-width:440px;margin:0 auto;">
            Ask questions about Python fundamentals, debugging errors, or click one of the quick action prompt chips below!
          </p>
        </div>
      `;
      return;
    }

    renderMessages(msgs);

  } catch (err) {
    messagesBox.innerHTML = `<div class="alert alert-error">${err.message}</div>`;
  }
}

function renderMessages(msgs) {
  const messagesBox = document.getElementById('chat-messages-box');
  if (!messagesBox) return;

  messagesBox.innerHTML = msgs.map(m => {
    const isUser = m.role === 'user';
    return `
      <div class="chat-msg ${isUser ? 'user' : 'assistant'}">
        <div class="msg-avatar">${isUser ? '👤' : '🤖'}</div>
        <div class="msg-bubble">
          ${renderMarkdown(m.content)}
        </div>
      </div>
    `;
  }).join('');

  messagesBox.scrollTop = messagesBox.scrollHeight;
}

async function handleSendMessage(actionType = null) {
  if (isSending || !activeSessionId) return;
  const textarea = document.getElementById('chat-user-input');
  const sendBtn = document.getElementById('btn-chat-send');
  const messagesBox = document.getElementById('chat-messages-box');

  const content = (textarea?.value || '').trim();
  if (!content) return;

  isSending = true;
  if (sendBtn) sendBtn.disabled = true;
  if (textarea) textarea.value = '';

  // Append user message optimistically
  const tempMsgHtml = `
    <div class="chat-msg user">
      <div class="msg-avatar">👤</div>
      <div class="msg-bubble">${escapeHtml(content)}</div>
    </div>
    <div class="chat-msg assistant" id="temp-thinking-msg">
      <div class="msg-avatar">🤖</div>
      <div class="msg-bubble" style="color:var(--text-muted);"><span class="loading-spin">⟳</span> Thinking…</div>
    </div>
  `;
  messagesBox.insertAdjacentHTML('beforeend', tempMsgHtml);
  messagesBox.scrollTop = messagesBox.scrollHeight;

  try {
    const reply = await mentorApi.send(activeSessionId, content, actionType);
    document.getElementById('temp-thinking-msg')?.remove();

    const assistantHtml = `
      <div class="chat-msg assistant animate-in">
        <div class="msg-avatar">🤖</div>
        <div class="msg-bubble">
          ${renderMarkdown(reply.content)}
        </div>
      </div>
    `;
    messagesBox.insertAdjacentHTML('beforeend', assistantHtml);
    messagesBox.scrollTop = messagesBox.scrollHeight;

  } catch (err) {
    document.getElementById('temp-thinking-msg')?.remove();
    showToast(err.message, 'error');
  } finally {
    isSending = false;
    if (sendBtn) sendBtn.disabled = false;
    textarea?.focus();
  }
}

function escapeHtml(str) {
  return (str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

