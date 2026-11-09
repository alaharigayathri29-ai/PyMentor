/**
 * assessment.js
 * Diagnostic Skill Assessment Controller (Real Multi-Page Application)
 * Authentic database questions, one-by-one test runner, and dynamic skill level calibration.
 */

import { requireAuth, initLayout, escapeHtml } from './common.js?v=20261108_v17';
import { assessmentApi } from './api.js?v=20261108_v17';
import { showToast } from './components/toast.js?v=20261108_v17';
import { showConfirmModal } from './components/modal.js?v=20261108_v17';
import { capitalize } from './utils/formatters.js?v=20261108_v17';

let questions = [];
let answers = {}; // { [question_id]: selected_option_index }
let currentIdx = 0;
let isSubmitting = false;
let currentCourse = 'python';

async function init() {
  const user = await requireAuth();
  if (!user) return;

  initLayout('assessment', user);

  // Setup Course Track Selector
  const courseButtons = document.querySelectorAll('#assess-course-selector button');
  courseButtons.forEach(btn => {
    btn.addEventListener('click', async () => {
      const selected = btn.getAttribute('data-course');
      if (selected === currentCourse) return;
      currentCourse = selected;
      courseButtons.forEach(b => b.classList.toggle('active', b === btn));
      
      const titleEl = document.getElementById('topbar-title');
      if (titleEl) {
        const titles = {
          python: 'Python Diagnostic Assessment',
          c: 'C Systems Diagnostic Assessment',
          cpp: 'Modern C++ Diagnostic Assessment',
          java: 'Enterprise Java Diagnostic Assessment',
        };
        titleEl.textContent = titles[selected] || 'Skill Assessment';
      }

      await loadQuestions(currentCourse);
    });
  });

  const prevBtn = document.getElementById('btn-assess-prev');
  const nextBtn = document.getElementById('btn-assess-next');
  const submitBtn = document.getElementById('btn-assess-submit');

  prevBtn?.addEventListener('click', () => {
    if (currentIdx > 0) {
      currentIdx--;
      renderActiveQuestion();
    }
  });

  nextBtn?.addEventListener('click', () => {
    if (currentIdx < questions.length - 1) {
      currentIdx++;
      renderActiveQuestion();
    }
  });

  submitBtn?.addEventListener('click', submitAssessment);

  // Check if student already has a previous assessment result; if query ?retake=1 is not present, show latest result or start fresh
  const urlParams = new URLSearchParams(window.location.search);
  const wantsRetake = urlParams.get('retake') === '1';

  if (!wantsRetake) {
    try {
      const existing = await assessmentApi.result();
      if (existing && existing.score !== null && existing.score !== undefined) {
        renderResults(existing);
        return;
      }
    } catch {}
  }

  // Load diagnostic questions
  await loadQuestions(currentCourse);
}

async function loadQuestions(course = 'python') {
  const quizBox = document.getElementById('assess-quiz-box');
  const resultsBox = document.getElementById('assess-results-box');
  const promptEl = document.getElementById('assess-question-prompt');

  if (quizBox) {
    quizBox.classList.remove('hidden');
    quizBox.style.display = 'block';
  }
  if (resultsBox) {
    resultsBox.classList.add('hidden');
    resultsBox.style.display = 'none';
  }
  if (promptEl) promptEl.textContent = 'Loading diagnostic assessment questions…';

  try {
    const data = await assessmentApi.questions(course);
    questions = Array.isArray(data) ? data : (data.questions || []);

    if (questions.length === 0) {
      if (promptEl) promptEl.textContent = 'No diagnostic questions found for this course track.';
      return;
    }

    answers = {};
    currentIdx = 0;
    renderActiveQuestion();
    buildQuestionPillNav();

  } catch (err) {
    if (promptEl) promptEl.textContent = `Error loading diagnostic test: ${err.message}`;
    showToast(`Error: ${err.message}`, 'error');
  }
}

function renderActiveQuestion() {
  if (questions.length === 0) return;
  const q = questions[currentIdx];

  const counterEl = document.getElementById('assess-q-counter');
  const topicTag = document.getElementById('assess-topic-tag');
  const progressFill = document.getElementById('assess-progress-fill');
  const promptEl = document.getElementById('assess-question-prompt');
  const optionsList = document.getElementById('assess-options-list');
  const prevBtn = document.getElementById('btn-assess-prev');
  const nextBtn = document.getElementById('btn-assess-next');
  const submitBtn = document.getElementById('btn-assess-submit');

  if (counterEl) counterEl.textContent = `Question ${currentIdx + 1} of ${questions.length}`;
  if (topicTag) topicTag.textContent = q.topic_name || capitalize(q.difficulty || 'Fundamentals');
  if (progressFill) {
    const pct = ((currentIdx + 1) / questions.length) * 100;
    progressFill.style.width = `${pct}%`;
  }
  if (promptEl) {
    const rawText = q.text || '';
    if (rawText.includes('```')) {
      const parts = rawText.split(/(```[a-z]*\n[\s\S]*?```)/g);
      promptEl.innerHTML = parts.map(part => {
        if (part.startsWith('```')) {
          const match = part.match(/```([a-z]*)\n([\s\S]*?)```/);
          const lang = match ? match[1] : '';
          const code = match ? match[2] : part.slice(3, -3);
          return `<pre style="background:#1C0E04;color:#FDE68A;padding:14px 18px;border-radius:10px;font-family:'JetBrains Mono',monospace;font-size:13px;overflow-x:auto;margin:14px 0;line-height:1.45;border:1.5px solid rgba(245,158,11,0.3);"><div style="font-size:10.5px;color:#94A3B8;text-transform:uppercase;margin-bottom:6px;font-weight:700;">${escapeHtml(lang || 'code')}</div><code>${escapeHtml(code)}</code></pre>`;
        }
        return `<div>${escapeHtml(part)}</div>`;
      }).join('');
    } else {
      promptEl.textContent = rawText;
    }
  }

  // Render options
  if (optionsList) {
    optionsList.innerHTML = (q.options || []).map((opt, optIdx) => {
      const isSelected = answers[q.id] === optIdx;
      return `
        <button class="quiz-option-card ${isSelected ? 'selected' : ''}" data-opt-idx="${optIdx}" style="display:flex;align-items:center;gap:14px;width:100%;padding:14px 18px;background:${isSelected ? 'var(--primary-light)' : '#FFFFFF'};border:1.5px solid ${isSelected ? 'var(--primary)' : 'var(--border)'};border-radius:var(--r-lg);margin-bottom:10px;cursor:pointer;text-align:left;transition:var(--transition);box-shadow:${isSelected ? '0 0 0 1px var(--primary)' : 'var(--shadow-xs)'};">
          <span style="width:28px;height:28px;border-radius:50%;background:${isSelected ? 'var(--primary)' : '#F1F5F9'};color:${isSelected ? '#FFFFFF' : 'var(--text-secondary)'};display:inline-flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;flex-shrink:0;">
            ${String.fromCharCode(65 + optIdx)}
          </span>
          <span style="font-size:14px;font-weight:500;color:var(--text-primary);">${escapeHtml(opt)}</span>
        </button>
      `;
    }).join('');

    optionsList.querySelectorAll('.quiz-option-card').forEach(btn => {
      btn.addEventListener('click', () => {
        const idx = parseInt(btn.getAttribute('data-opt-idx'), 10);
        answers[q.id] = idx;
        renderActiveQuestion();
        updatePillNavStatus();
      });
    });
  }

  // Prev / Next / Submit button visibility
  if (prevBtn) prevBtn.disabled = currentIdx === 0;
  const isLast = currentIdx === questions.length - 1;
  if (nextBtn) nextBtn.classList.toggle('hidden', isLast);
  if (submitBtn) submitBtn.classList.toggle('hidden', !isLast);

  updatePillNavStatus();
}

function buildQuestionPillNav() {
  const container = document.getElementById('assess-pills-container');
  if (!container) return;

  container.innerHTML = questions.map((q, idx) => {
    const isCur = idx === currentIdx;
    const isAns = answers[q.id] !== undefined;
    return `
      <button class="quiz-num-pill ${isCur ? 'active' : ''} ${isAns ? 'answered' : ''}" data-idx="${idx}" style="width:34px;height:34px;border-radius:var(--r-md);background:${isCur ? 'var(--primary)' : (isAns ? 'var(--secondary-light)' : '#FFFFFF')};border:1.5px solid ${isCur ? 'var(--primary)' : (isAns ? 'var(--secondary)' : 'var(--border)')};color:${isCur ? '#FFFFFF' : (isAns ? 'var(--secondary)' : 'var(--text-secondary)')};font-size:12px;font-weight:700;cursor:pointer;">
        ${idx + 1}
      </button>
    `;
  }).join('');

  container.querySelectorAll('.quiz-num-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      currentIdx = parseInt(btn.getAttribute('data-idx'), 10);
      renderActiveQuestion();
    });
  });
}

function updatePillNavStatus() {
  const pills = document.querySelectorAll('.quiz-num-pill');
  pills.forEach((p, idx) => {
    const q = questions[idx];
    const isAnswered = answers[q?.id] !== undefined;
    const isCurrent = idx === currentIdx;

    if (isCurrent) {
      p.style.background = 'var(--primary)';
      p.style.borderColor = 'var(--primary)';
      p.style.color = '#FFFFFF';
    } else if (isAnswered) {
      p.style.background = 'var(--secondary-light)';
      p.style.borderColor = 'var(--secondary)';
      p.style.color = 'var(--secondary)';
    } else {
      p.style.background = '#FFFFFF';
      p.style.borderColor = 'var(--border)';
      p.style.color = 'var(--text-secondary)';
    }
  });
}

async function submitAssessment() {
  if (isSubmitting) return;

  const answeredCount = Object.keys(answers).length;
  if (answeredCount < questions.length) {
    const ok = await showConfirmModal({
      title: 'Incomplete Assessment',
      message: `You have answered ${answeredCount} of ${questions.length} questions. Submit anyway?`,
      confirmText: 'Submit Anyway',
      cancelText: 'Continue Answering',
    });
    if (!ok) return;
  }

  isSubmitting = true;
  const submitBtn = document.getElementById('btn-assess-submit');
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>Grading & Calibrating…</span>';
  }

  // Format payload for backend AssessmentSubmit schema:
  // answers: [{ question_id: int, answer: str }]
  const payload = Object.entries(answers).map(([qId, optIdx]) => ({
    question_id: parseInt(qId, 10),
    answer: String(optIdx),
  }));

  try {
    const res = await assessmentApi.submit(payload, currentCourse);
    showToast('Diagnostic assessment completed and skill path calibrated!', 'success');
    renderResults(res);
  } catch (err) {
    showToast(`Submission failed: ${err.message}`, 'error');
  } finally {
    isSubmitting = false;
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<span>Submit Assessment ✓</span>';
    }
  }
}

function renderResults(result) {
  const quizBox = document.getElementById('assess-quiz-box');
  const resultsBox = document.getElementById('assess-results-box');
  const resSkill = document.getElementById('res-skill-level');
  const resScore = document.getElementById('res-score');

  if (quizBox) {
    quizBox.classList.add('hidden');
    quizBox.style.display = 'none';
  }
  if (resultsBox) {
    resultsBox.classList.remove('hidden');
    resultsBox.style.display = 'block';
  }

  const score = Math.round(result.score || 0);
  if (resScore) resScore.textContent = `${score}%`;
  if (resSkill) {
    resSkill.textContent = `${capitalize(result.skill_level || 'beginner')} Track`;
  }
}

init();
