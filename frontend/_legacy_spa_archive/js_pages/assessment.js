/**
 * Diagnostic Assessment Controller.
 * One-by-one question display with instant state updates.
 */

import { assessmentApi } from '../api.js';
import { showToast } from '../components/toast.js';
import { capitalize } from '../utils/formatters.js';

let questions = [];
let answers = {};
let currentIdx = 0;
let isSubmitting = false;

export async function initAssessment() {
  const introCard = document.getElementById('assessment-intro-card');
  const quizCard = document.getElementById('assessment-quiz-card');
  const resultCard = document.getElementById('assessment-result-card');
  const startBtn = document.getElementById('btn-start-assessment');
  const prevBtn = document.getElementById('btn-quiz-prev');
  const nextBtn = document.getElementById('btn-quiz-next');
  const submitBtn = document.getElementById('btn-quiz-submit');
  const retakeBtn = document.getElementById('btn-retake-assessment');

  // Check if student already has a previous assessment result
  try {
    const existing = await assessmentApi.result();
    if (existing && existing.score !== null) {
      renderResults(existing);
      return;
    }
  } catch {}

  // Show intro
  introCard?.classList.remove('hidden');
  quizCard?.classList.add('hidden');
  resultCard?.classList.add('hidden');

  startBtn?.addEventListener('click', startAssessment);
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
  retakeBtn?.addEventListener('click', startAssessment);
}

async function startAssessment() {
  const introCard = document.getElementById('assessment-intro-card');
  const quizCard = document.getElementById('assessment-quiz-card');
  const resultCard = document.getElementById('assessment-result-card');

  introCard?.classList.add('hidden');
  resultCard?.classList.add('hidden');
  quizCard?.classList.remove('hidden');

  try {
    questions = await assessmentApi.questions();
    answers = {};
    currentIdx = 0;
    isSubmitting = false;
    renderActiveQuestion();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

function renderActiveQuestion() {
  if (!questions || questions.length === 0) return;
  const q = questions[currentIdx];
  const total = questions.length;
  const pct = Math.round(((currentIdx + 1) / total) * 100);

  const topicTag = document.getElementById('quiz-topic-tag');
  const counter = document.getElementById('quiz-question-counter');
  const progText = document.getElementById('quiz-progress-text');
  const progFill = document.getElementById('quiz-progress-fill');
  const qText = document.getElementById('quiz-question-text');
  const optContainer = document.getElementById('quiz-options-container');
  const answeredCount = document.getElementById('quiz-answered-count');
  const prevBtn = document.getElementById('btn-quiz-prev');
  const nextBtn = document.getElementById('btn-quiz-next');
  const submitBtn = document.getElementById('btn-quiz-submit');

  if (topicTag) topicTag.textContent = q.topic || 'Python Core';
  if (counter) counter.textContent = `Question ${currentIdx + 1} of ${total}`;
  if (progText) progText.textContent = `${pct}%`;
  if (progFill) progFill.style.width = `${pct}%`;

  if (qText) {
    qText.innerHTML = q.text
      .replace(/```python\n?([\s\S]*?)```/g, '<pre style="margin:10px 0;padding:12px;background:#090d18;border:1px solid rgba(255,255,255,0.08);border-radius:8px;"><code>$1</code></pre>')
      .replace(/`([^`]+)`/g, '<code style="background:rgba(255,255,255,0.08);padding:2px 6px;border-radius:4px;color:#c084fc;">$1</code>');
  }

  // Render option buttons
  if (optContainer) {
    optContainer.innerHTML = (q.options || []).map((opt, i) => {
      const isSelected = answers[q.id] === String(i);
      return `
        <button class="quiz-option-btn ${isSelected ? 'correct' : ''}" data-opt-idx="${i}" onclick="window.selectQuizOption(${q.id}, '${i}')">
          <span style="width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:${isSelected ? 'var(--purple)' : 'rgba(255,255,255,0.06)'};color:#fff;font-weight:700;font-size:12px;">${'ABCD'[i]}</span>
          <span>${opt}</span>
        </button>
      `;
    }).join('');
  }

  // Answered tally
  const ansCount = Object.keys(answers).length;
  if (answeredCount) answeredCount.textContent = `${ansCount} of ${total} answered`;

  // Buttons state
  if (prevBtn) prevBtn.disabled = currentIdx === 0;
  if (currentIdx === total - 1) {
    nextBtn?.classList.add('hidden');
    submitBtn?.classList.remove('hidden');
  } else {
    nextBtn?.classList.remove('hidden');
    submitBtn?.classList.add('hidden');
  }

  window.selectQuizOption = (qid, idxStr) => {
    answers[qid] = idxStr;
    renderActiveQuestion();
  };
}

async function submitAssessment() {
  if (isSubmitting) return;

  const total = questions.length;
  const answered = Object.keys(answers).length;
  if (answered < total) {
    const proceed = confirm(`You have answered ${answered} of ${total} questions. Would you like to submit anyway?`);
    if (!proceed) return;
  }

  isSubmitting = true;
  const submitBtn = document.getElementById('btn-quiz-submit');
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.textContent = 'Calculating score…';
  }

  const payload = Object.entries(answers).map(([qid, ans]) => ({
    question_id: parseInt(qid),
    answer: ans,
  }));

  try {
    const result = await assessmentApi.submit(payload);
    showToast('Assessment submitted successfully!', 'success');
    renderResults(result);
  } catch (err) {
    showToast(err.message, 'error');
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Submit Assessment ✓';
    }
    isSubmitting = false;
  }
}

function renderResults(result) {
  const introCard = document.getElementById('assessment-intro-card');
  const quizCard = document.getElementById('assessment-quiz-card');
  const resultCard = document.getElementById('assessment-result-card');

  introCard?.classList.add('hidden');
  quizCard?.classList.add('hidden');
  resultCard?.classList.remove('hidden');

  const scorePct = document.getElementById('res-score-pct');
  const scoreSub = document.getElementById('res-score-sub');
  const tierName = document.getElementById('res-tier-name');
  const tierDesc = document.getElementById('res-tier-desc');
  const topicsList = document.getElementById('res-topics-list');
  const badgeIcon = document.getElementById('res-badge-icon');

  const tier = result.skill_level || 'beginner';
  const score = Math.round(result.score || 0);

  if (scorePct) scorePct.textContent = `${score}%`;
  if (scoreSub) scoreSub.textContent = `${result.correct_answers || 0} of ${result.total_questions || 6} correct`;
  if (tierName) tierName.textContent = capitalize(tier);

  const tierMeta = {
    beginner: {
      icon: '🌱',
      desc: 'Solid foundation start! Your curriculum will focus on Python syntax, variables, conditionals, and loops.',
    },
    intermediate: {
      icon: '⚡',
      desc: 'Great proficiency! Your curriculum is calibrated for data structures, functions, comprehensions, and OOP.',
    },
    advanced: {
      icon: '🚀',
      desc: 'Mastery demonstrated! Your curriculum will emphasize advanced patterns, error handling, algorithms, and projects.',
    },
  };

  const meta = tierMeta[tier] || tierMeta.beginner;
  if (badgeIcon) badgeIcon.textContent = meta.icon;
  if (tierDesc) tierDesc.textContent = meta.desc;

  if (topicsList) {
    const scores = result.topic_scores || {};
    const entries = Object.entries(scores);
    if (entries.length > 0) {
      topicsList.innerHTML = entries.map(([slug, pct]) => `
        <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:rgba(255,255,255,0.02);border:1px solid var(--border);border-radius:6px;font-size:13px;">
          <span style="text-transform:capitalize;">${slug.replace(/-/g, ' ')}</span>
          <span style="font-weight:700;color:${pct >= 70 ? '#4ade80' : pct >= 40 ? '#fde047' : '#fca5a5'};">${Math.round(pct)}%</span>
        </div>
      `).join('');
    } else {
      topicsList.innerHTML = '<span style="font-size:12px;color:var(--text-muted);">Topic breakdown recorded.</span>';
    }
  }

  // Update topbar level badge
  const tbBadge = document.getElementById('topbar-level-badge');
  if (tbBadge) tbBadge.textContent = capitalize(tier);
}

