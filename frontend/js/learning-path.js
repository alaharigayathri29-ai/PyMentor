/**
 * learning-path.js
 * Curriculum Roadmap Controller (Real Multi-Page Application)
 * Loads real topics and modules from backend database via GET /api/learning-path/curriculum
 */

import { requireAuth, initLayout } from './common.js?v=20261108_v17';
import { learningPathApi } from './api.js?v=20261108_v17';
import { capitalize } from './utils/formatters.js?v=20261108_v17';

async function init() {
  const user = await requireAuth();
  if (!user) return;

  initLayout('learning-path', user);

  const container = document.getElementById('curriculum-modules-container') || document.getElementById('lp-modules-container');
  const skillBadge = document.getElementById('path-level-badge') || document.getElementById('lp-skill-badge');
  const progPct = document.getElementById('curriculum-completion-pct') || document.getElementById('lp-progress-pct');
  const progLabel = document.getElementById('lp-progress-label');
  const progFill = document.getElementById('lp-progress-fill');

  if (!container) {
    console.error('[LearningPath] Curriculum modules container not found in DOM.');
    return;
  }
  container.innerHTML = `<div style="padding:60px;text-align:center;color:var(--text-muted);"><div class="spinner" style="margin:0 auto 16px;"></div>Loading Python Curriculum…</div>`;

  try {
    const data = await learningPathApi.curriculum();
    const modules = data.modules || [];

    if (skillBadge) {
      skillBadge.textContent = `${capitalize(data.skill_level || 'beginner')} Track`;
    }

    // Calculate overall completed count
    let totalTopics = 0;
    let completedTopics = 0;
    modules.forEach(m => {
      (m.topics || []).forEach(t => {
        totalTopics++;
        if (t.status === 'completed') completedTopics++;
      });
    });

    const completionRate = totalTopics > 0 ? Math.round((completedTopics / totalTopics) * 100) : 0;
    if (progLabel) progLabel.textContent = `Track Progress: ${completedTopics} of ${totalTopics} Topics Mastered`;
    if (progPct) progPct.textContent = `${completionRate}%`;
    if (progFill) progFill.style.width = `${completionRate}%`;

    // Render Modules
    container.innerHTML = modules.map((m, mIdx) => {
      const topics = m.topics || [];
      const modCompleted = topics.filter(t => t.status === 'completed').length;

      return `
        <div class="module-group-card">
          <div class="module-header-bar" onclick="window.toggleModuleAccordion(${m.module_number})">
            <div style="display:flex;align-items:center;gap:14px;">
              <div class="module-badge-num">${m.module_number}</div>
              <div>
                <h3 style="font-size:16px;font-weight:700;color:var(--text-primary);margin:0;">Module ${m.module_number}: ${m.module_name}</h3>
                <div style="font-size:12px;color:var(--text-muted);margin-top:2px;">
                  ${modCompleted}/${topics.length} topics completed
                </div>
              </div>
            </div>
            <div style="display:flex;align-items:center;gap:12px;">
              <span class="badge ${modCompleted === topics.length ? 'badge-green' : (modCompleted > 0 ? 'badge-blue' : 'badge-gray')}">
                ${modCompleted === topics.length ? 'Mastered ✓' : (modCompleted > 0 ? 'In Progress' : 'Available')}
              </span>
              <span id="module-arrow-${m.module_number}" style="font-size:14px;color:var(--text-muted);">▼</span>
            </div>
          </div>

          <div id="module-body-${m.module_number}" style="display:flex;flex-direction:column;">
            ${topics.map((t, tIdx) => {
              const isLocked = t.status === 'locked';
              const isDone = t.status === 'completed';
              const isCurrent = t.is_current || t.status === 'in_progress' || (t.status === 'available' && tIdx === 0 && mIdx === 0);

              let starsHtml = '';
              if (t.mastery_score >= 80) starsHtml = '⭐⭐⭐';
              else if (t.mastery_score >= 50) starsHtml = '⭐⭐';
              else if (t.mastery_score > 0) starsHtml = '⭐';

              return `
                <div class="topic-node-row ${isCurrent ? 'current-active' : ''}">
                  <div style="display:flex;align-items:center;gap:14px;min-width:0;flex:1;">
                    <div class="topic-icon-bubble ${isDone ? 'completed' : ''}">
                      ${isDone ? '✓' : (isLocked ? '🔒' : (t.icon || '📚'))}
                    </div>
                    <div style="min-width:0;flex:1;">
                      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                        <h4 style="font-size:14.5px;font-weight:700;color:var(--text-primary);margin:0;">${t.name}</h4>
                        ${starsHtml ? `<span style="font-size:11px;">${starsHtml}</span>` : ''}
                        ${isCurrent ? '<span class="badge badge-purple" style="font-size:9px;">ACTIVE</span>' : ''}
                        ${t.lesson_completed ? '<span class="badge badge-green" style="font-size:9px;">LESSON DONE</span>' : ''}
                      </div>
                      <div style="font-size:12px;color:var(--text-secondary);margin-top:3px;text-overflow:ellipsis;overflow:hidden;white-space:nowrap;">
                        ${(t.subtopics || []).slice(0, 3).join(' • ') || t.description}
                      </div>
                    </div>
                  </div>

                  <div style="display:flex;align-items:center;gap:14px;flex-shrink:0;">
                    ${!isLocked ? `
                      <div style="text-align:right;min-width:80px;">
                        <div style="font-size:12px;font-weight:700;color:${t.mastery_score >= 70 ? 'var(--success)' : 'var(--primary)'};">${t.mastery_score}%</div>
                        <div style="font-size:10px;color:var(--text-muted);">Mastery</div>
                      </div>
                      <a href="/lesson.html?id=${t.id}" class="btn ${isCurrent ? 'btn-primary' : 'btn-secondary'} btn-sm" style="text-decoration:none;">
                        <span>${isDone ? 'Review Lesson' : (isCurrent ? '⚡ Study Lesson' : 'Open Lesson')}</span>
                      </a>
                    ` : `
                      <button class="btn btn-ghost btn-sm" disabled style="opacity:0.4;">
                        <span>🔒 Locked</span>
                      </button>
                    `}
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        </div>
      `;
    }).join('');

    window.toggleModuleAccordion = (modNum) => {
      const body = document.getElementById(`module-body-${modNum}`);
      const arrow = document.getElementById(`module-arrow-${modNum}`);
      if (!body) return;
      const isHidden = body.style.display === 'none';
      body.style.display = isHidden ? 'flex' : 'none';
      if (arrow) arrow.textContent = isHidden ? '▼' : '►';
    };

  } catch (err) {
    container.innerHTML = `<div class="alert alert-error">Failed to load curriculum: ${err.message}</div>`;
  }
}

init();
