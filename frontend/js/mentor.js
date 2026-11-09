/**
 * mentor.js
 * AI Mentor Chat Controller (Real Multi-Page Application)
 * Interactive AI tutoring with Google Gemini live responses,
 * Multi-Language Chat Support & Voice Assistant (Speech-to-Text & Text-to-Speech).
 */

import { requireAuth, initLayout, escapeHtml } from './common.js?v=20261108_v17';
import { mentorApi } from './api.js?v=20261108_v17';
import { renderMarkdown } from './utils/markdown.js?v=20261108_v17';
import { showToast } from './components/toast.js?v=20261108_v17';
import { formatRelative } from './utils/formatters.js?v=20261108_v17';

let sessions = [];
let activeSessionId = null;
let isSending = false;
let currentUser = null;

// Multi-Language & Voice Assistant State
let currentLang = localStorage.getItem('pym_mentor_lang') || 'en';
let isAutoSpeak = localStorage.getItem('pym_autospeak') === 'true';
let recognition = null;
let isListening = false;
let currentlySpeakingBtn = null;

const SPEECH_LANG_MAP = {
  en: 'en-US',
  hi: 'hi-IN',
  te: 'te-IN',
  ta: 'ta-IN',
  kn: 'kn-IN',
  bn: 'bn-IN',
  es: 'es-ES',
  fr: 'fr-FR',
  de: 'de-DE',
};

const LANG_PLACEHOLDERS = {
  en: 'Ask your Python question or speak via microphone… (Press Enter to send)',
  hi: 'अपना पायथन प्रश्न पूछें या माइक से बोलें… (Enter दबाकर भेजें)',
  te: 'మీ పైథాన్ ప్రశ్నను అడగండి లేదా మైక్ ద్వారా మాట్లాడండి… (పంపడానికి Enter నొక్కండి)',
  ta: 'உங்கள் பைதான் கேள்வியைக் கேளுங்கள் அல்லது மைக் மூலம் பேசுங்கள்…',
  kn: 'ನಿಮ್ಮ ಪೈಥಾನ್ ಪ್ರಶ್ನೆಯನ್ನು ಕೇಳಿ ಅಥವಾ ಮೈಕ್ ಮೂಲಕ ಮಾತನಾಡಿ…',
  bn: 'আপনার পাইথন প্রশ্ন জিজ্ঞাসা করুন বা মাইক্রোফোনে কথা বলুন…',
  es: 'Haz tu pregunta sobre Python o habla por el micrófono…',
  fr: 'Posez votre question sur Python ou parlez au micro…',
  de: 'Stelle deine Python-Frage oder sprich ins Mikrofon…',
};

async function init() {
  const user = await requireAuth();
  if (!user) return;
  currentUser = user;

  initLayout('mentor', user);

  const sidebar = document.getElementById('mentor-sidebar');
  const toggleBtn = document.getElementById('btn-toggle-sidebar');
  const newBtn = document.getElementById('btn-mentor-new');
  const deleteBtn = document.getElementById('btn-delete-session');
  const sendBtn = document.getElementById('btn-chat-send');
  const textarea = document.getElementById('chat-user-input');
  const chips = document.querySelectorAll('.action-chip');
  const modeIndicator = document.getElementById('chat-mode-indicator');
  const langSelect = document.getElementById('mentor-language-select');
  const micBtn = document.getElementById('btn-voice-mic');
  const cancelVoiceBtn = document.getElementById('btn-cancel-voice');
  const autoSpeakBtn = document.getElementById('btn-toggle-autospeak');
  const stopSpeechBtn = document.getElementById('btn-stop-speech');

  // Initialize Language Selector
  if (langSelect) {
    langSelect.value = currentLang;
    langSelect.addEventListener('change', (e) => {
      currentLang = e.target.value;
      localStorage.setItem('pym_mentor_lang', currentLang);
      updateInputPlaceholder();
      stopSpeech();
      showToast(`Language set to ${langSelect.options[langSelect.selectedIndex].text}`, 'info');
    });
  }
  updateInputPlaceholder();

  // Initialize Auto-Speak Button State
  updateAutoSpeakUI();
  autoSpeakBtn?.addEventListener('click', () => {
    isAutoSpeak = !isAutoSpeak;
    localStorage.setItem('pym_autospeak', isAutoSpeak);
    updateAutoSpeakUI();
    if (!isAutoSpeak) stopSpeech();
    showToast(`Auto Speak ${isAutoSpeak ? 'Enabled' : 'Disabled'}`, 'info');
  });

  // Global Stop Audio Button
  stopSpeechBtn?.addEventListener('click', () => {
    stopSpeech();
    showToast('Audio playback stopped.', 'info');
  });

  // Initialize Speech Recognition (Voice Assistant Input)
  initSpeechRecognition();
  micBtn?.addEventListener('click', toggleVoiceInput);
  cancelVoiceBtn?.addEventListener('click', stopVoiceInput);

  // Check AI Provider mode from backend
  try {
    const st = await mentorApi.status();
    if (modeIndicator) {
      modeIndicator.textContent = st.is_mock
        ? 'Offline Educational Model'
        : `Connected to ${st.model || 'AI'}`;
    }
  } catch {}

  // Sidebar toggle
  toggleBtn?.addEventListener('click', () => {
    sidebar?.classList.toggle('collapsed');
  });

  // New Chat
  newBtn?.addEventListener('click', async () => {
    try {
      const newSess = await mentorApi.newSession('New Chat');
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
        explain: 'Can you please explain this concept with an engaging analogy and real-world example?',
        debug: 'Can you help me analyze why this error occurs and how to fix it step-by-step?',
        example: 'Can you show a clear, practical, and runnable Python code example for this topic?',
        quiz: 'Can you ask me a conceptual quiz question to test my understanding of this topic?',
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

  // Load conversations from database
  await loadSessions();
}

function updateInputPlaceholder() {
  const textarea = document.getElementById('chat-user-input');
  if (textarea) {
    textarea.placeholder = LANG_PLACEHOLDERS[currentLang] || LANG_PLACEHOLDERS.en;
  }
}

function updateAutoSpeakUI() {
  const icon = document.getElementById('autospeak-icon');
  const text = document.getElementById('autospeak-text');
  const btn = document.getElementById('btn-toggle-autospeak');
  if (icon) icon.textContent = isAutoSpeak ? '🔊' : '🔈';
  if (text) text.textContent = `Auto Speak: ${isAutoSpeak ? 'On' : 'Off'}`;
  if (btn) btn.style.color = isAutoSpeak ? 'var(--primary)' : 'var(--text-secondary)';
}

// ── Multi-Language Auto-Detection & Speech Engine ─────────────────────────

function detectScriptLanguage(text) {
  if (!text) return null;
  // Telugu script (\u0C00-\u0C7F)
  if (/[\u0C00-\u0C7F]/.test(text)) return 'te';
  // Devanagari / Hindi script (\u0900-\u097F)
  if (/[\u0900-\u097F]/.test(text)) return 'hi';
  // Tamil script (\u0B80-\u0BFF)
  if (/[\u0B80-\u0BFF]/.test(text)) return 'ta';
  // Kannada script (\u0C80-\u0CFF)
  if (/[\u0C80-\u0CFF]/.test(text)) return 'kn';
  // Bengali script (\u0980-\u09FF)
  if (/[\u0980-\u09FF]/.test(text)) return 'bn';
  // Romanized Telugu keywords
  if (/\b(enti|cheppandi|cheppu|ela|gurinchi|kavali|ardham|chudandi|yemi|telugu)\b/i.test(text)) return 'te';
  // Romanized Hindi keywords
  if (/\b(kya hai|batao|kaise|karo|samjhao|mujhe|chahiye|hindi)\b/i.test(text)) return 'hi';
  // Spanish keywords or accents
  if (/[áéíóúñ¿¡]|\b(hola|por favor|explicar|como|que es|espanol)\b/i.test(text)) return 'es';
  // French keywords or accents
  if (/[àâçèéêëîïôùûü]|\b(bonjour|merci|comment|francais)\b/i.test(text)) return 'fr';
  // German keywords or umlauts
  if (/[äöüß]|\b(hallo|bitte|deutsch)\b/i.test(text)) return 'de';
  return null;
}

// ── Voice Assistant: Speech-to-Text (Voice Recognition) ──────────────────────

function initSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    console.warn('[Voice Assistant] Web Speech API not supported in this browser.');
    return;
  }

  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = true;

  recognition.onstart = () => {
    isListening = true;
    const micBtn = document.getElementById('btn-voice-mic');
    const banner = document.getElementById('voice-status-banner');
    const statusText = document.getElementById('voice-status-text');
    micBtn?.classList.add('listening');
    if (banner) {
      banner.classList.remove('hidden');
      banner.style.display = 'flex';
    }
    if (statusText) {
      const langNames = {
        en: 'English',
        hi: 'Hindi (हिंदी)',
        te: 'Telugu (తెలుగు)',
        ta: 'Tamil (தமிழ்)',
        kn: 'Kannada (ಕನ್ನಡ)',
        bn: 'Bengali (বাংলা)',
        es: 'Spanish (Español)',
        fr: 'French (Français)',
        de: 'German (Deutsch)'
      };
      statusText.textContent = `Listening... Speak in ${langNames[currentLang] || 'English'}`;
    }
  };

  recognition.onresult = (event) => {
    const textarea = document.getElementById('chat-user-input');
    let transcript = '';
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      transcript += event.results[i][0].transcript;
    }
    if (textarea && transcript) {
      textarea.value = transcript;
      // Auto-detect language if student spoke in a different language
      const detected = detectScriptLanguage(transcript);
      if (detected && detected !== currentLang) {
        currentLang = detected;
        localStorage.setItem('pym_mentor_lang', currentLang);
        const langSelect = document.getElementById('mentor-language-select');
        if (langSelect) langSelect.value = currentLang;
        updateInputPlaceholder();
      }
    }
  };

  recognition.onerror = (event) => {
    console.warn('[Voice Assistant] Speech recognition error:', event.error);
    if (event.error === 'not-allowed') {
      showToast('Microphone permission denied. Please allow microphone access in browser settings.', 'error');
    }
    stopVoiceInput();
  };

  recognition.onend = () => {
    stopVoiceInput();
  };
}

function toggleVoiceInput() {
  if (!recognition) {
    showToast('Voice input is not supported in this browser. Please use Chrome or Edge.', 'warn');
    return;
  }

  if (isListening) {
    recognition.stop();
  } else {
    // Stop active speech before listening
    stopSpeech();
    recognition.lang = SPEECH_LANG_MAP[currentLang] || 'en-US';
    try {
      recognition.start();
    } catch (err) {
      console.warn('[Voice Assistant] Recognition already started or error:', err);
    }
  }
}

function stopVoiceInput() {
  isListening = false;
  const micBtn = document.getElementById('btn-voice-mic');
  const banner = document.getElementById('voice-status-banner');
  micBtn?.classList.remove('listening');
  if (banner) {
    banner.classList.add('hidden');
    banner.style.display = 'none';
  }
}

// ── Voice Assistant: Text-to-Speech (Speaking AI Mentor) ─────────────────────

// Keep voices updated when browser finishes loading speech synth voices
if ('speechSynthesis' in window) {
  window.speechSynthesis.onvoiceschanged = () => {
    // Warm up voice cache
    window.speechSynthesis.getVoices();
  };
}

function findBestVoiceForLang(langCode) {
  if (!('speechSynthesis' in window)) return null;
  const voices = window.speechSynthesis.getVoices();
  if (!voices || voices.length === 0) return null;

  const targetLang = (SPEECH_LANG_MAP[langCode] || 'en-US').toLowerCase();
  const prefix = targetLang.split('-')[0];

  const nameKeywords = {
    te: ['telugu', 'తెలుగు', 'mohan', 'shruti'],
    hi: ['hindi', 'हिन्दी', 'swara', 'madhur'],
    ta: ['tamil', 'தமிழ்', 'valluvar'],
    kn: ['kannada', 'ಕನ್ನಡ', 'gagan'],
    bn: ['bengali', 'বাংলা', 'bashkar'],
    es: ['spanish', 'español', 'elena', 'jorge'],
    fr: ['french', 'français', 'paul', 'julie'],
    de: ['german', 'deutsch', 'stefan', 'hedda'],
    en: ['english', 'natural', 'google', 'david', 'mark', 'zira', 'neerja'],
  };

  const keywords = nameKeywords[langCode] || [prefix];

  // 1. First priority: Online/Natural or Google native voice for target language
  const highQualityNative = voices.find(v => {
    const vLang = v.lang.toLowerCase();
    const vName = v.name.toLowerCase();
    const langMatch = vLang === targetLang || vLang.startsWith(prefix);
    const qualityMatch = vName.includes('natural') || vName.includes('online') || vName.includes('google');
    return langMatch && qualityMatch;
  });
  if (highQualityNative) return highQualityNative;

  // 2. Second priority: Any voice matching target language code or prefix
  const anyLangMatch = voices.find(v => {
    const vLang = v.lang.toLowerCase();
    return vLang === targetLang || vLang.startsWith(prefix);
  });
  if (anyLangMatch) return anyLangMatch;

  // 3. Third priority: Voice name containing target language keywords
  const nameMatch = voices.find(v => {
    const vName = v.name.toLowerCase();
    return keywords.some(k => vName.includes(k));
  });
  if (nameMatch) return nameMatch;

  // 4. Fourth priority for Indian languages: Indian English voice (e.g. en-IN or Neerja)
  if (['te', 'hi', 'ta', 'kn', 'bn'].includes(langCode)) {
    const indianVoice = voices.find(v => v.lang.toLowerCase() === 'en-in' || v.name.toLowerCase().includes('india') || v.name.toLowerCase().includes('neerja'));
    if (indianVoice) return indianVoice;
  }

  // 5. Default browser voice fallback
  return voices.find(v => v.default) || voices[0] || null;
}

function cleanTextForSpeech(raw, langCode = 'en') {
  if (!raw) return [];

  const codeAnnouncements = {
    te: 'కోడ్ ఉదాహరణ స్క్రీన్‌పై చూపించబడింది.',
    hi: 'कोड उदाहरण स्क्रीन पर दिखाया गया है।',
    ta: 'குறியீடு உதாரணம் திரையில் காட்டப்பட்டுள்ளது.',
    kn: 'ಕೋಡ್ ಉದಾಹರಣೆ ಪರದೆಯ ಮೇಲೆ ತೋರಿಸಲಾಗಿದೆ.',
    bn: 'কোড উদাহরণ স্ক্রিনে দেখানো হয়েছে।',
    es: 'El ejemplo de código se muestra en pantalla.',
    fr: "L'exemple de code est affiché à l'écran.",
    de: 'Das Codebeispiel wird auf dem Bildschirm angezeigt.',
    en: 'The code example is shown on screen.',
  };
  const codePhrase = codeAnnouncements[langCode] || codeAnnouncements.en;

  let text = raw
    .replace(/```[\s\S]*?```/g, ` ${codePhrase} `)
    .replace(/`([^`]+)`/g, '$1')                                         // inline code
    .replace(/\*\*([^*]+)\*\*/g, '$1')                                   // bold
    .replace(/\*([^*]+)\*/g, '$1')                                       // italics
    .replace(/^#+\s+/gm, '')                                             // headers
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')                             // link text
    .replace(/^[-*•]\s+/gm, '')                                          // bullets
    .replace(/^\d+\.\s+/gm, '')                                          // list numbers
    .replace(/---+/g, '')                                                // dividers
    .replace(/[🤖👤👋📦💡🚀⚙️🎉🍕🔍🍎🍌]/gu, '')                           // emoji cleaner
    .trim();

  // Split into natural sentence chunks to prevent utterance timeouts in Chrome/Edge
  const rawSentences = text.split(/(?<=[.?!।\n])\s+/);
  const sentences = [];
  for (let s of rawSentences) {
    const trimmed = s.trim();
    if (!trimmed) continue;
    if (trimmed.length > 180) {
      const parts = trimmed.split(/[,،;]\s+/);
      for (const p of parts) {
        const pt = p.trim();
        if (pt) sentences.push(pt);
      }
    } else {
      sentences.push(trimmed);
    }
  }
  return sentences.length > 0 ? sentences : [text];
}

let speechQueue = [];
let speechQueueIndex = 0;
let isQueuePlaying = false;

function speakMessage(text, playBtn = null, forcedLang = null) {
  if (!('speechSynthesis' in window)) {
    showToast('Text-to-speech audio is not supported in this browser.', 'warn');
    return;
  }

  // Toggle off if currently speaking this button
  if (window.speechSynthesis.speaking && currentlySpeakingBtn === playBtn) {
    stopSpeech();
    return;
  }

  // Stop previous utterance
  stopSpeech();

  // Determine speech language: explicit forcedLang, detected from text script, or currentLang
  const lang = forcedLang || detectScriptLanguage(text) || currentLang || 'en';
  const sentences = cleanTextForSpeech(text, lang);
  if (!sentences || sentences.length === 0) return;

  const stopBtn = document.getElementById('btn-stop-speech');
  if (playBtn) {
    currentlySpeakingBtn = playBtn;
    playBtn.classList.add('speaking');
    playBtn.innerHTML = '<span>⏹ Speaking…</span>';
  }
  stopBtn?.classList.remove('hidden');

  speechQueue = sentences;
  speechQueueIndex = 0;
  isQueuePlaying = true;

  playNextInQueue(lang, playBtn);
}

function playNextInQueue(langCode, playBtn) {
  if (!isQueuePlaying || speechQueueIndex >= speechQueue.length) {
    resetSpeakingUI();
    return;
  }

  const textChunk = speechQueue[speechQueueIndex];
  speechQueueIndex++;

  const utterance = new SpeechSynthesisUtterance(textChunk);
  const targetLang = SPEECH_LANG_MAP[langCode] || 'en-US';
  utterance.lang = targetLang;
  utterance.rate = 0.96; // clear natural pedagogical pacing
  utterance.pitch = 1.0;

  const matchedVoice = findBestVoiceForLang(langCode);
  if (matchedVoice) {
    utterance.voice = matchedVoice;
  }

  utterance.onend = () => {
    if (isQueuePlaying) {
      playNextInQueue(langCode, playBtn);
    }
  };

  utterance.onerror = (e) => {
    console.warn('[Voice Assistant] TTS chunk error:', e);
    if (isQueuePlaying && speechQueueIndex < speechQueue.length) {
      playNextInQueue(langCode, playBtn);
    } else {
      resetSpeakingUI();
    }
  };

  window.speechSynthesis.speak(utterance);
}

function stopSpeech() {
  isQueuePlaying = false;
  speechQueue = [];
  speechQueueIndex = 0;
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
  resetSpeakingUI();
}

function resetSpeakingUI() {
  isQueuePlaying = false;
  const stopBtn = document.getElementById('btn-stop-speech');
  if (currentlySpeakingBtn) {
    currentlySpeakingBtn.classList.remove('speaking');
    currentlySpeakingBtn.innerHTML = '<span>🔊 Listen</span>';
    currentlySpeakingBtn = null;
  }
  stopBtn?.classList.add('hidden');
}

// ── Sessions & Messaging ─────────────────────────────────────────────────────

async function loadSessions(selectId = null) {
  const container = document.getElementById('mentor-sessions-container');
  const messagesBox = document.getElementById('chat-messages-box');
  if (!container) return;
  container.innerHTML = `<div style="padding:20px;text-align:center;color:var(--text-muted);"><div class="spinner" style="margin:0 auto 10px;"></div></div>`;

  try {
    sessions = await mentorApi.sessions();

    if (!sessions || sessions.length === 0) {
      container.innerHTML = `
        <div style="padding:24px 16px;text-align:center;color:var(--text-secondary);">
          <div style="font-size:32px;margin-bottom:8px;">🤖</div>
          <div style="font-size:14px;font-weight:700;color:var(--text-primary);">No conversations yet</div>
          <p style="font-size:12px;color:var(--text-secondary);margin:4px 0 14px;">Start a conversation with your AI Python Mentor.</p>
          <button class="btn btn-primary btn-sm btn-full" id="btn-start-first-conv">Start New Conversation</button>
        </div>
      `;

      document.getElementById('btn-start-first-conv')?.addEventListener('click', async () => {
        try {
          const first = await mentorApi.newSession('Python Learning');
          await loadSessions(first.id);
        } catch (err) {
          showToast(err.message, 'error');
        }
      });

      if (messagesBox) {
        messagesBox.innerHTML = `
          <div style="text-align:center;padding:60px 20px;color:var(--text-secondary);">
            <div style="font-size:48px;margin-bottom:12px;">👋</div>
            <h3 style="font-size:18px;color:var(--text-primary);margin-bottom:8px;">Welcome to AI Voice Mentor</h3>
            <p style="font-size:13.5px;max-width:460px;margin:0 auto 20px;line-height:1.6;">
              Your personalized multi-language Python tutor. Speak via microphone or type questions in your preferred language!
            </p>
          </div>
        `;
      }
      return;
    }

    container.innerHTML = sessions.map(s => `
      <div class="session-item ${s.id === (selectId || activeSessionId || sessions[0].id) ? 'active' : ''}" data-session-id="${s.id}">
        <div style="min-width:0;flex:1;">
          <div class="session-title">
            ${escapeHtml(s.title || 'New Session')}
          </div>
          <div class="session-meta">${formatRelative(s.created_at)}</div>
        </div>
      </div>
    `).join('');

    container.querySelectorAll('.session-item').forEach(item => {
      item.addEventListener('click', () => {
        const id = parseInt(item.getAttribute('data-session-id'), 10);
        container.querySelectorAll('.session-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        openSession(id);
      });
    });

    const targetId = selectId || activeSessionId || sessions[0].id;
    await openSession(targetId);

  } catch (err) {
    container.innerHTML = `<div class="alert alert-error" style="margin:12px;">${err.message}</div>`;
  }
}

async function openSession(sessionId) {
  stopSpeech();
  activeSessionId = sessionId;
  const messagesBox = document.getElementById('chat-messages-box');
  const sessionTitle = document.getElementById('chat-session-title');
  if (!messagesBox) return;

  const currentSess = sessions.find(s => s.id === sessionId);
  if (sessionTitle && currentSess) {
    sessionTitle.textContent = currentSess.title || 'Python Mentor';
  }

  messagesBox.innerHTML = `<div style="padding:60px;text-align:center;color:var(--text-muted);"><div class="spinner" style="margin:0 auto 10px;"></div></div>`;

  try {
    const msgs = await mentorApi.messages(sessionId);
    if (!msgs || msgs.length === 0) {
      messagesBox.innerHTML = `
        <div class="chat-empty-state" style="text-align:center;padding:48px 20px;color:var(--text-secondary);">
          <div style="font-size:48px;margin-bottom:12px;">💬</div>
          <h3 style="font-size:16px;color:var(--text-primary);margin-bottom:6px;">How can I help you today?</h3>
          <p style="font-size:13px;max-width:440px;margin:0 auto;">
            Ask questions, click a quick action chip, or speak with the microphone in your preferred language!
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

  const studentName = (currentUser?.username === 'honey_qis')
    ? 'A.sri Lakshmi Gayatri'
    : (currentUser?.username || 'You');

  messagesBox.innerHTML = msgs.map((m, idx) => {
    const isUser = m.role === 'user';
    return `
      <div class="chat-message-row ${isUser ? 'user-row' : 'assistant-row'}">
        <div class="chat-avatar">${isUser ? '👤' : '🤖'}</div>
        <div class="chat-bubble ${isUser ? 'user-bubble' : 'assistant-bubble'}">
          <div class="chat-bubble-author">
            <span>${isUser ? escapeHtml(studentName) : 'PyMentor'}</span>
            ${!isUser ? `<button class="btn-speech-play" data-msg-idx="${idx}" title="Listen to response"><span>🔊 Listen</span></button>` : ''}
          </div>
          <div class="chat-bubble-content markdown-body">
            ${isUser ? escapeHtml(m.content) : renderMarkdown(m.content)}
          </div>
        </div>
      </div>
    `;
  }).join('');

  // Bind listen buttons on assistant messages
  messagesBox.querySelectorAll('.btn-speech-play').forEach(btn => {
    btn.addEventListener('click', () => {
      const idx = parseInt(btn.getAttribute('data-msg-idx'), 10);
      const msg = msgs[idx];
      if (msg) {
        const msgLang = detectScriptLanguage(msg.content) || currentLang;
        speakMessage(msg.content, btn, msgLang);
      }
    });
  });

  messagesBox.scrollTop = messagesBox.scrollHeight;
}

async function handleSendMessage(action = 'chat') {
  if (isSending) return;
  const textarea = document.getElementById('chat-user-input');
  const sendBtn = document.getElementById('btn-chat-send');
  const messagesBox = document.getElementById('chat-messages-box');
  const content = textarea?.value.trim();

  if (!content) return;

  // Auto-detect input language if student typed or spoke native script
  const detected = detectScriptLanguage(content);
  if (detected && detected !== currentLang) {
    currentLang = detected;
    localStorage.setItem('pym_mentor_lang', currentLang);
    const langSelect = document.getElementById('mentor-language-select');
    if (langSelect) langSelect.value = currentLang;
    updateInputPlaceholder();
    const langName = langSelect?.options[langSelect.selectedIndex]?.text || currentLang;
    showToast(`Language set to ${langName} — responding in native voice!`, 'info');
  }

  if (!activeSessionId) {
    const newSess = await mentorApi.newSession('New Chat');
    sessions.unshift(newSess);
    activeSessionId = newSess.id;
    await loadSessions(newSess.id);
  }

  isSending = true;
  if (sendBtn) {
    sendBtn.disabled = true;
    sendBtn.innerHTML = '<span>…</span>';
  }

  // Clear empty state prompt if present
  const emptyPrompt = messagesBox?.querySelector('.chat-empty-state');
  if (emptyPrompt) emptyPrompt.remove();

  // Optimistically append user message to UI
  const studentName = (currentUser?.username === 'honey_qis')
    ? 'A.sri Lakshmi Gayatri'
    : (currentUser?.username || 'You');

  const tempUserRow = document.createElement('div');
  tempUserRow.className = 'chat-message-row user-row';
  tempUserRow.innerHTML = `
    <div class="chat-avatar">👤</div>
    <div class="chat-bubble user-bubble">
      <div class="chat-bubble-author">${escapeHtml(studentName)}</div>
      <div class="chat-bubble-content">${escapeHtml(content)}</div>
    </div>
  `;
  messagesBox?.appendChild(tempUserRow);

  // Append typing indicator
  const typingRow = document.createElement('div');
  typingRow.className = 'chat-message-row assistant-row typing-row';
  typingRow.innerHTML = `
    <div class="chat-avatar">🤖</div>
    <div class="chat-bubble assistant-bubble">
      <div class="chat-bubble-author">PyMentor</div>
      <div class="chat-bubble-content" style="display:flex;align-items:center;gap:6px;padding:8px 0;">
        <span class="spinner" style="width:14px;height:14px;"></span>
        <span style="font-size:12px;color:var(--text-muted);">Consulting AI Mentor…</span>
      </div>
    </div>
  `;
  messagesBox?.appendChild(typingRow);
  if (messagesBox) messagesBox.scrollTop = messagesBox.scrollHeight;

  if (textarea) textarea.value = '';

  try {
    const sendFn = mentorApi.sendMessage || mentorApi.send;
    if (!sendFn) {
      throw new Error('Mentor API send function not found in client.');
    }

    // Send content with student's active language
    const aiResp = await sendFn.call(mentorApi, activeSessionId, content, action, currentLang);
    typingRow.remove();

    // Update active session title if modified by AI auto-titling
    if (aiResp.session_title) {
      const sessObj = sessions.find(s => s.id === activeSessionId);
      if (sessObj) sessObj.title = aiResp.session_title;
      const sessionTitle = document.getElementById('chat-session-title');
      if (sessionTitle) sessionTitle.textContent = aiResp.session_title;
      const activeEl = document.querySelector(`.session-item[data-session-id="${activeSessionId}"] .session-title`);
      if (activeEl) activeEl.textContent = aiResp.session_title;
    }

    const responseLang = aiResp.language || detectScriptLanguage(aiResp.content) || currentLang;

    const aiRow = document.createElement('div');
    aiRow.className = 'chat-message-row assistant-row';
    aiRow.innerHTML = `
      <div class="chat-avatar">🤖</div>
      <div class="chat-bubble assistant-bubble">
        <div class="chat-bubble-author">
          <span>PyMentor</span>
          <button class="btn-speech-play" title="Listen to response"><span>🔊 Listen</span></button>
        </div>
        <div class="chat-bubble-content markdown-body">
          ${renderMarkdown(aiResp.content)}
        </div>
      </div>
    `;
    messagesBox?.appendChild(aiRow);

    const playBtn = aiRow.querySelector('.btn-speech-play');
    playBtn?.addEventListener('click', () => {
      speakMessage(aiResp.content, playBtn, responseLang);
    });

    // Auto-Speak if enabled
    if (isAutoSpeak) {
      speakMessage(aiResp.content, playBtn, responseLang);
    }

    if (messagesBox) messagesBox.scrollTop = messagesBox.scrollHeight;

  } catch (err) {
    typingRow.remove();
    console.error('[Mentor] Error in message exchange:', err);

    // In-chat error bubble
    const errRow = document.createElement('div');
    errRow.className = 'chat-message-row assistant-row error-row';
    errRow.innerHTML = `
      <div class="chat-avatar">⚠️</div>
      <div class="chat-bubble assistant-bubble" style="border-left: 3px solid var(--danger);background:#FFF5F5;">
        <div class="chat-bubble-author" style="color:var(--danger);">PyMentor Error</div>
        <div class="chat-bubble-content">
          <p style="color:var(--danger);font-weight:600;font-size:13px;margin-bottom:4px;">Failed to receive AI response</p>
          <p style="font-size:12px;color:var(--text-secondary);">${escapeHtml(err.message)}</p>
        </div>
      </div>
    `;
    messagesBox?.appendChild(errRow);
    showToast(`AI Mentor: ${err.message}`, 'error');
  } finally {
    isSending = false;
    if (sendBtn) {
      sendBtn.disabled = false;
      sendBtn.innerHTML = '<span>Send ↑</span>';
    }
  }
}

init();
