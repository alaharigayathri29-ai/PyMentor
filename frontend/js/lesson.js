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
      const examples = lesson.examples || lesson.code_examples || [];
      if (examples.length > 0) {
        exList.innerHTML = examples.map((ex, idx) => `
          <div class="code-demo-card">
            <div class="code-demo-header">
              <span style="font-weight:600;color:var(--text-primary);">Example ${idx + 1}: ${ex.title || 'Code Demonstration'}</span>
              <button class="btn btn-ghost btn-sm btn-run-playground" data-example-idx="${idx}">
                <span>▶ Open in Playground</span>
              </button>
            </div>
            <pre style="margin:0;padding:16px;background:#2A1A0C;color:#F5E6D3;font-family:'JetBrains Mono',monospace;font-size:13px;line-height:1.6;overflow-x:auto;"><code>${escapeHtml(ex.code || '')}</code></pre>
            <div class="demo-output-box">
              <div style="font-size:10px;text-transform:uppercase;color:var(--text-muted);margin-bottom:4px;letter-spacing:0.05em;">Expected Output</div>
              <div>${escapeHtml(ex.output || ex.expected_output || '')}</div>
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
      const quizzes = lesson.quizzes || lesson.practice_questions || [];
      if (quizzes.length > 0) {
        quizList.innerHTML = quizzes.map((q, qIdx) => {
          const correctIdx = q.correct_index !== undefined ? q.correct_index : q.correct_answer;
          return `
          <div class="lesson-quiz-container" id="quiz-block-${qIdx}">
            <div style="font-weight:700;font-size:14px;color:var(--text-primary);margin-bottom:12px;">
              Question ${qIdx + 1}: ${q.question}
            </div>
            <div class="quiz-options-list">
              ${(q.options || []).map((opt, optIdx) => `
                <button class="quiz-option-btn" data-qid="${qIdx}" data-oidx="${optIdx}" data-correct="${correctIdx}">
                  <span style="width:22px;height:22px;border-radius:50%;background:rgba(255,255,255,0.06);display:inline-flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;">
                    ${String.fromCharCode(65 + optIdx)}
                  </span>
                  <span>${opt}</span>
                </button>
              `).join('')}
            </div>
            <div class="quiz-feedback-box hidden" id="quiz-feedback-${qIdx}" style="margin-top:12px;padding:12px 14px;border-radius:var(--r-md);font-size:13px;"></div>
          </div>
        `;
        }).join('');

        quizList.querySelectorAll('.quiz-option-btn').forEach(btn => {
          btn.addEventListener('click', () => {
            const qIdx = parseInt(btn.getAttribute('data-qid'), 10);
            const oIdx = parseInt(btn.getAttribute('data-oidx'), 10);
            const targetCorrect = parseInt(btn.getAttribute('data-correct'), 10);
            const q = quizzes[qIdx];
            const feedEl = document.getElementById(`quiz-feedback-${qIdx}`);

            btn.parentElement.querySelectorAll('.quiz-option-btn').forEach(b => {
              b.classList.remove('selected', 'correct', 'wrong');
              b.disabled = true;
            });

            if (oIdx === targetCorrect) {
              btn.classList.add('correct');
              if (feedEl) {
                feedEl.className = 'quiz-feedback-box';
                feedEl.style.background = 'rgba(16, 185, 129, 0.15)';
                feedEl.style.border = '1px solid rgba(16, 185, 129, 0.3)';
                feedEl.style.color = '#059669';
                feedEl.innerHTML = `<strong>Correct!</strong> ${q.explanation || 'Well done!'}`;
                feedEl.classList.remove('hidden');
              }
            } else {
              btn.classList.add('wrong');
              const correctBtn = btn.parentElement.querySelector(`[data-oidx="${targetCorrect}"]`);
              if (correctBtn) correctBtn.classList.add('correct');
              if (feedEl) {
                feedEl.className = 'quiz-feedback-box';
                feedEl.style.background = 'rgba(239, 68, 68, 0.15)';
                feedEl.style.border = '1px solid rgba(239, 68, 68, 0.3)';
                feedEl.style.color = '#DC2626';
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

    // ── PDF & Markdown Study Guide Downloads ───────────────────────────────────
    const triggerPdfDownload = () => {
      const watermarkUser = document.getElementById('pdf-watermark-user');
      const watermarkDate = document.getElementById('pdf-watermark-date');
      const now = new Date();
      if (watermarkUser) watermarkUser.textContent = `Student: ${user.username || user.name || 'Verified Scholar'}`;
      if (watermarkDate) watermarkDate.textContent = `Generated: ${now.toLocaleDateString(undefined, { dateStyle: 'long' })}`;
      showToast('Opening print dialog. Select "Save as PDF" to save your study guide.', 'info');
      setTimeout(() => {
        window.print();
      }, 250);
    };

    document.getElementById('btn-download-pdf')?.addEventListener('click', triggerPdfDownload);
    document.getElementById('btn-topbar-download-pdf')?.addEventListener('click', triggerPdfDownload);

    document.getElementById('btn-download-markdown')?.addEventListener('click', () => {
      const examples = lesson.examples || lesson.code_examples || [];
      const objectives = topic.learning_objectives || [];
      const subtopics = topic.subtopics || [];

      let md = `# PyMentor Study Guide — ${topic.name}\n`;
      md += `**Module ${topic.module_number || 1}**: ${topic.module_name || 'Curriculum'}\n`;
      md += `**Difficulty**: ${capitalize(topic.difficulty || 'beginner')}\n`;
      md += `**Subtopics**: ${subtopics.join(', ')}\n\n`;
      md += `---\n\n`;
      md += `## 🎯 Learning Objectives\n`;
      objectives.forEach(obj => { md += `- ${obj}\n`; });
      md += `\n---\n\n`;
      md += `## 📖 Overview\n${lesson.introduction || ''}\n\n`;
      md += `## 📚 In-Depth Topic Notes & Deep Dive\n${lesson.explanation || ''}\n\n`;
      if (examples.length > 0) {
        md += `## 💻 Code Demonstrations\n`;
        examples.forEach((ex, idx) => {
          md += `### Example ${idx + 1}: ${ex.title || 'Demonstration'}\n`;
          md += `\`\`\`python\n${ex.code || ''}\n\`\`\`\n\n`;
          md += `**Expected Output:**\n\`\`\`\n${ex.output || ex.expected_output || ''}\n\`\`\`\n\n`;
          if (ex.explanation) md += `*Explanation*: ${ex.explanation}\n\n`;
        });
      }
      md += `\n---\n*Generated by PyMentor Academic Platform for ${user.username || 'Student'} on ${new Date().toLocaleDateString()}*\n`;

      const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `PyMentor_${topic.slug || 'topic'}_Study_Guide.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      showToast('Downloaded Markdown Study Guide!', 'success');
    });

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

