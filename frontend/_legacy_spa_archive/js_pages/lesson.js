/**
 * Interactive Lesson Controller.
 * BYJU'S Structured Lesson Experience with practical code demonstrations.
 */

import { learningPathApi } from '../api.js';
import { renderMarkdown } from '../utils/markdown.js';
import { showToast } from '../components/toast.js';
import { capitalize } from '../utils/formatters.js';

export async function initLesson() {
  // Extract topic_id from hash query string #lesson?topic_id=X or sessionStorage
  let topicId = 1;
  const hash = window.location.hash;
  if (hash.includes('topic_id=')) {
    const parsed = parseInt(hash.split('topic_id=')[1], 10);
    if (!isNaN(parsed)) topicId = parsed;
  } else {
    const saved = sessionStorage.getItem('current_lesson_topic_id');
    if (saved) topicId = parseInt(saved, 10);
  }

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
        objList.innerHTML = objectives.map((obj, i) => `
          <div class="objective-item">
            <span style="color:var(--green);font-weight:700;">✓</span>
            <span>${obj}</span>
          </div>
        `).join('');
      } else {
        objList.innerHTML = '<div class="objective-item"><span>Understand fundamental mechanics and syntax.</span></div>';
      }
    }

    // In-Depth Conceptual Explanation
    if (expEl) {
      expEl.innerHTML = lesson.explanation
        ? renderMarkdown(lesson.explanation)
        : `<p>Review standard documentation and practical patterns for ${topic.name}.</p>`;
    }

    // Practical Code Examples with Outputs & "Try in Playground"
    if (exList) {
      const examples = lesson.code_examples || [];
      if (examples.length > 0) {
        exList.innerHTML = examples.map((ex, i) => `
          <div class="code-demo-box">
            <div class="code-demo-header">
              <span style="font-weight:600;font-size:12.5px;color:#fff;">Example ${i + 1}: ${ex.title || 'Code Demonstration'}</span>
              <button class="btn btn-primary btn-sm" onclick="window.runExampleInPlayground(${i})" style="font-size:11px;padding:3px 10px;">
                <span>▶ Open in Playground</span>
              </button>
            </div>
            <pre class="code-demo-content"><code>${escapeHtml(ex.code || '')}</code></pre>
            ${ex.expected_output ? `
              <div class="output-demo-content">
                <div style="font-size:10px;text-transform:uppercase;color:var(--text-muted);font-weight:700;margin-bottom:4px;">Expected Output:</div>
                <pre style="margin:0;font-family:inherit;font-size:inherit;color:#4ade80;">${escapeHtml(ex.expected_output)}</pre>
              </div>
            ` : ''}
          </div>
        `).join('');

        window.runExampleInPlayground = (exIdx) => {
          const ex = examples[exIdx];
          if (!ex) return;
          sessionStorage.setItem('playground_code', ex.code);
          showToast('Loaded into Playground! Switching...', 'info');
          window.location.hash = '#playground';
        };
      } else {
        exList.innerHTML = '<div style="font-size:13px;color:var(--text-muted);">Interactive examples ready in the Practice Lab.</div>';
      }
    }

    // Check Your Understanding Quiz Questions
    if (quizList) {
      const questions = lesson.practice_questions || [];
      if (questions.length > 0) {
        quizList.innerHTML = questions.map((q, qIdx) => `
          <div style="margin-bottom:20px;padding:16px;background:rgba(255,255,255,0.02);border:1px solid var(--border);border-radius:10px;">
            <div style="font-size:14px;font-weight:600;color:#fff;margin-bottom:12px;">Q${qIdx + 1}. ${q.question}</div>
            <div>
              ${(q.options || []).map((opt, oIdx) => `
                <button class="quiz-option-btn" id="quiz-${qIdx}-opt-${oIdx}" onclick="window.checkLessonQuiz(${qIdx}, ${oIdx}, ${q.correct_answer})">
                  <span style="font-weight:700;font-size:12px;">${'ABCD'[oIdx]}.</span>
                  <span>${opt}</span>
                </button>
              `).join('')}
            </div>
            <div id="quiz-${qIdx}-feedback" style="display:none;margin-top:10px;font-size:12.5px;padding:8px 12px;border-radius:6px;"></div>
          </div>
        `).join('');

        window.checkLessonQuiz = (qIdx, selectedIdx, correctIdx) => {
          const fb = document.getElementById(`quiz-${qIdx}-feedback`);
          const q = questions[qIdx];
          const isCorrect = selectedIdx === correctIdx;

          for (let i = 0; i < (q.options || []).length; i++) {
            const btn = document.getElementById(`quiz-${qIdx}-opt-${i}`);
            if (btn) {
              btn.classList.remove('correct', 'wrong');
              if (i === correctIdx) btn.classList.add('correct');
              else if (i === selectedIdx && !isCorrect) btn.classList.add('wrong');
            }
          }

          if (fb) {
            fb.style.display = 'block';
            if (isCorrect) {
              fb.style.background = 'rgba(16, 185, 129, 0.15)';
              fb.style.color = '#6ee7b7';
              fb.innerHTML = `✓ <strong>Correct!</strong> ${q.explanation || ''}`;
            } else {
              fb.style.background = 'rgba(239, 68, 68, 0.15)';
              fb.style.color = '#fca5a5';
              fb.innerHTML = `✗ <strong>Try again:</strong> ${q.explanation || ''}`;
            }
          }
        };
      } else {
        quizList.innerHTML = '<div style="font-size:13px;color:var(--text-muted);">Proceed to the coding practice exercises to verify your understanding.</div>';
      }
    }

    // Complete Lesson Button
    if (completeBtn) {
      if (topic.lesson_completed) {
        completeBtn.textContent = '✓ Lesson Completed';
        completeBtn.disabled = true;
      } else {
        completeBtn.disabled = false;
        completeBtn.onclick = async () => {
          try {
            completeBtn.disabled = true;
            completeBtn.textContent = 'Updating progress…';
            await learningPathApi.completeLesson(topicId);
            showToast('Lesson marked complete! +50 XP awarded.', 'success');
            completeBtn.textContent = '✓ Lesson Completed';
          } catch (err) {
            showToast(err.message, 'error');
            completeBtn.disabled = false;
            completeBtn.textContent = '✓ Mark Lesson Completed (+50 XP)';
          }
        };
      }
    }

    // Practice button jumps to practice lab with this topic
    if (practiceBtn) {
      practiceBtn.onclick = () => {
        sessionStorage.setItem('practice_topic_id', topicId);
        window.location.hash = '#practice';
      };
    }

  } catch (err) {
    showToast(err.message, 'error');
  }
}

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

