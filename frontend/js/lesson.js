/**
 * lesson.js
 * Interactive Lesson Controller (Real Multi-Page Application)
 * Loads real topic curriculum lesson content from GET /api/learning-path/topics/{id}
 */

import { requireAuth, initLayout } from './common.js?v=20261108_v17';
import { learningPathApi } from './api.js?v=20261108_v17';
import { renderMarkdown } from './utils/markdown.js?v=20261108_v17';
import { showToast } from './components/toast.js?v=20261108_v17';
import { capitalize } from './utils/formatters.js?v=20261108_v17';

async function init() {
  const user = await requireAuth();
  if (!user) return;

  initLayout('lesson', user);

  // Extract topic ID from URL search params: /lesson.html?id=2 or /lesson.html?topic_id=2
  const params = new URLSearchParams(window.location.search);
  let topicId = parseInt(params.get('id') || params.get('topic_id') || '1', 10);
  if (isNaN(topicId) || topicId < 1) topicId = 1;

  const titleEl = document.getElementById('lesson-title');
  const modTag = document.getElementById('lesson-module-tag');
  const diffTag = document.getElementById('lesson-diff-tag');
  const iconEl = document.getElementById('lesson-icon');
  const subtopicsEl = document.getElementById('lesson-subtopics');
  const introEl = document.getElementById('lesson-intro');
  const objList = document.getElementById('lesson-objectives-list');
  const expEl = document.getElementById('lesson-explanation');
  const exList = document.getElementById('lesson-examples-list');
  const quizList = document.getElementById('lesson-quiz-list');
  const completeBtn = document.getElementById('btn-complete-lesson');
  const practiceBtn = document.getElementById('btn-practice-topic');

  try {
    const topic = await learningPathApi.getTopicLesson(topicId);
    const lesson = topic.lesson_content || {};

    if (titleEl) titleEl.textContent = topic.name;
    if (modTag) modTag.textContent = `Module ${topic.module_number || 1}: ${topic.module_name || 'Core'}`;
    if (diffTag) diffTag.textContent = capitalize(topic.difficulty || 'beginner');
    if (iconEl) iconEl.textContent = topic.icon || '📚';
    if (subtopicsEl) subtopicsEl.textContent = (topic.subtopics || []).join(' • ');

    if (introEl) {
      introEl.innerHTML = lesson.introduction
        ? renderMarkdown(lesson.introduction)
        : `Welcome to <strong>${topic.name}</strong>. Learn core concepts through interactive code demonstrations and guided practice.`;
    }

    // Learning Objectives Checklist
    if (objList) {
      const objectives = topic.learning_objectives || [];
      if (objectives.length > 0) {
        objList.innerHTML = objectives.map(obj => `
          <div class="objective-item" style="display:flex;align-items:center;gap:10px;padding:8px 0;font-size:13.5px;color:var(--text-primary);">
            <span style="color:var(--green);font-weight:700;">✓</span>
            <span>${obj}</span>
          </div>
        `).join('');
      } else {
        objList.innerHTML = '<div style="font-size:13px;color:var(--text-muted);">Understand concepts, review practical examples, and complete assessment.</div>';
      }
    }

    // Comprehensive Explanation Markdown
    if (expEl) {
      expEl.innerHTML = lesson.explanation
        ? renderMarkdown(lesson.explanation)
        : '<p style="color:var(--text-muted);">Lesson content is currently being prepared for this topic.</p>';
    }

    // Runnable Practical Examples
    if (exList) {
      const examples = lesson.examples || [];
      if (examples.length > 0) {
        exList.innerHTML = examples.map((ex, idx) => `
          <div class="code-demo-card">
            <div class="code-demo-header">
              <span style="font-weight:600;color:var(--text-primary);">Example ${idx + 1}: ${ex.title || 'Code Demonstration'}</span>
              <button class="btn btn-ghost btn-sm btn-run-playground" data-example-idx="${idx}">
                <span>▶ Open in Playground</span>
              </button>
            </div>
            <pre style="margin:0;padding:16px;background:#FFFFFF;color:var(--text-primary);font-family:'JetBrains Mono',monospace;font-size:13px;line-height:1.6;overflow-x:auto;"><code>${escapeHtml(ex.code || '')}</code></pre>
            <div class="demo-output-box">
              <div style="font-size:10px;text-transform:uppercase;color:var(--text-muted);margin-bottom:4px;letter-spacing:0.05em;">Expected Output</div>
              <div>${escapeHtml(ex.output || '')}</div>
            </div>
          </div>
        `).join('');

        exList.querySelectorAll('.btn-run-playground').forEach(btn => {
          btn.addEventListener('click', () => {
            const idx = parseInt(btn.getAttribute('data-example-idx'), 10);
            const ex = examples[idx];
            if (ex && ex.code) {
              sessionStorage.setItem('playground_code', ex.code);
              window.location.href = '/playground.html';
            }
          });
        });
      } else {
        exList.innerHTML = '<div style="font-size:13px;color:var(--text-muted);padding:14px 0;">Practical examples for this module will appear here.</div>';
      }
    }

    // Interactive Knowledge Check / Quizzes
    if (quizList) {
      const quizzes = lesson.quizzes || [];
      if (quizzes.length > 0) {
        quizList.innerHTML = quizzes.map((q, qIdx) => `
          <div class="lesson-quiz-container" id="quiz-block-${qIdx}">
            <div style="font-weight:700;font-size:14px;color:var(--text-primary);margin-bottom:12px;">
              Question ${qIdx + 1}: ${q.question}
            </div>
            <div class="quiz-options-list">
              ${(q.options || []).map((opt, optIdx) => `
                <button class="quiz-option-btn" data-qid="${qIdx}" data-oidx="${optIdx}">
                  <span style="width:22px;height:22px;border-radius:50%;background:rgba(255,255,255,0.06);display:inline-flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;">
                    ${String.fromCharCode(65 + optIdx)}
                  </span>
                  <span>${opt}</span>
                </button>
              `).join('')}
            </div>
            <div class="quiz-feedback-box hidden" id="quiz-feedback-${qIdx}" style="margin-top:12px;padding:12px 14px;border-radius:var(--r-md);font-size:13px;"></div>
          </div>
        `).join('');

        quizList.querySelectorAll('.quiz-option-btn').forEach(btn => {
          btn.addEventListener('click', () => {
            const qIdx = parseInt(btn.getAttribute('data-qid'), 10);
            const oIdx = parseInt(btn.getAttribute('data-oidx'), 10);
            const q = quizzes[qIdx];
            const feedEl = document.getElementById(`quiz-feedback-${qIdx}`);

            btn.parentElement.querySelectorAll('.quiz-option-btn').forEach(b => {
              b.classList.remove('selected', 'correct', 'wrong');
              b.disabled = true;
            });

            if (oIdx === q.correct_index) {
              btn.classList.add('correct');
              if (feedEl) {
                feedEl.className = 'quiz-feedback-box';
                feedEl.style.background = 'rgba(16, 185, 129, 0.15)';
                feedEl.style.border = '1px solid rgba(16, 185, 129, 0.3)';
                feedEl.style.color = '#4ade80';
                feedEl.innerHTML = `<strong>Correct!</strong> ${q.explanation || ''}`;
                feedEl.classList.remove('hidden');
              }
            } else {
              btn.classList.add('wrong');
              const correctBtn = btn.parentElement.querySelector(`[data-oidx="${q.correct_index}"]`);
              if (correctBtn) correctBtn.classList.add('correct');
              if (feedEl) {
                feedEl.className = 'quiz-feedback-box';
                feedEl.style.background = 'rgba(239, 68, 68, 0.15)';
                feedEl.style.border = '1px solid rgba(239, 68, 68, 0.3)';
                feedEl.style.color = '#f87171';
                feedEl.innerHTML = `<strong>Incorrect.</strong> ${q.explanation || ''}`;
                feedEl.classList.remove('hidden');
              }
            }
          });
        });
      } else {
        quizList.innerHTML = '<div style="font-size:13px;color:var(--text-muted);">No quiz questions attached to this topic.</div>';
      }
    }

    // Mark as Completed Button Handler
    if (completeBtn) {
      if (topic.student_status === 'completed' || topic.lesson_completed) {
        completeBtn.classList.remove('btn-primary');
        completeBtn.classList.add('btn-secondary');
        completeBtn.innerHTML = '<span>✓ Lesson Completed</span>';
      }

      completeBtn.addEventListener('click', async () => {
        completeBtn.disabled = true;
        completeBtn.innerHTML = '<span>Saving progress…</span>';
        try {
          await learningPathApi.completeLesson(topicId);
          showToast('Lesson marked complete! Topic mastery updated.', 'success');
          completeBtn.classList.remove('btn-primary');
          completeBtn.classList.add('btn-secondary');
          completeBtn.innerHTML = '<span>✓ Lesson Completed</span>';
        } catch (err) {
          showToast(err.message, 'error');
          completeBtn.disabled = false;
          completeBtn.innerHTML = '<span>✓ Mark Lesson as Completed</span>';
        }
      });
    }

    // Practice Button Handler
    if (practiceBtn) {
      practiceBtn.href = `/practice.html?topic_id=${topicId}`;
    }

  } catch (err) {
    showToast(`Failed to load topic lesson: ${err.message}`, 'error');
  }
}

function escapeHtml(str) {
  return (str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

init();

