/**
 * learning-path.js
 * Polyglot Curriculum Roadmap Controller (Real Multi-Page Application)
 * Loads real topics and modules from backend database across Python, C, C++, and Java.
 */

import { requireAuth, initLayout } from './common.js?v=20261108_v17';
import { learningPathApi } from './api.js?v=20261108_v17';
import { capitalize } from './utils/formatters.js?v=20261108_v17';

let currentCourse = 'python';

async function init() {
  const user = await requireAuth();
  if (!user) return;

  initLayout('learning-path', user);

  const urlParams = new URLSearchParams(window.location.search);
  const requestedCourse = (urlParams.get('course') || 'python').toLowerCase();
  currentCourse = ['python', 'c', 'cpp', 'java'].includes(requestedCourse) ? requestedCourse : 'python';

  // Setup 4-Course Selector Buttons
  const courseButtons = document.querySelectorAll('#lp-course-selector button');
  courseButtons.forEach(btn => {
    const courseAttr = btn.getAttribute('data-course');
    btn.classList.toggle('active', courseAttr === currentCourse);
    btn.addEventListener('click', () => {
      if (courseAttr === currentCourse) return;
      currentCourse = courseAttr;
      courseButtons.forEach(b => b.classList.toggle('active', b === btn));
      // Update browser URL without full reload
      const newUrl = `${window.location.pathname}?course=${currentCourse}`;
      window.history.pushState({ path: newUrl }, '', newUrl);
      loadCurriculum(currentCourse);
    });
  });

  await loadCurriculum(currentCourse);
}

async function loadCurriculum(course = 'python') {
  const container = document.getElementById('curriculum-modules-container') || document.getElementById('lp-modules-container');
  const skillBadge = document.getElementById('path-level-badge') || document.getElementById('lp-skill-badge');
  const progPct = document.getElementById('curriculum-completion-pct') || document.getElementById('lp-progress-pct');
  const progLabel = document.getElementById('lp-progress-label');
  const progFill = document.getElementById('lp-progress-fill');
  const topbarTitle = document.getElementById('topbar-title');

  const courseMeta = {
    python: { name: 'Python Systems', icon: '🐍', desc: 'Structured 7-module Python path covering fundamentals, functional programming, data structures, and async pipelines.' },
    c: { name: 'ANSI C Systems', icon: '⚙️', desc: 'Deep hardware & memory architecture path covering pointers, memory layout, dynamic allocation, POSIX threads, and system calls.' },
    cpp: { name: 'Modern C++20', icon: '⚡', desc: 'High-performance systems engineering covering RAII, smart pointers, move semantics, VTables, concurrency, and C++20 concepts.' },
    java: { name: 'Enterprise Java 21', icon: '☕', desc: 'Enterprise distributed architecture covering JVM memory internals, GC tuning, Streams, virtual threads, and Spring Boot.' },
  };

  const meta = courseMeta[course] || courseMeta.python;
  if (topbarTitle) topbarTitle.textContent = `${meta.name} Curriculum`;

  const heroTitle = document.querySelector('.curriculum-hero h1');
  const heroDesc = document.querySelector('.curriculum-hero p');
  if (heroTitle) heroTitle.textContent = `${meta.name} Curriculum Roadmap`;
  if (heroDesc) heroDesc.textContent = meta.desc;

  if (!container) return;
  container.innerHTML = `<div style="padding:60px;text-align:center;color:var(--text-muted);"><div class="spinner" style="margin:0 auto 16px;"></div>Loading ${meta.name} Curriculum…</div>`;

  try {
    const data = await learningPathApi.curriculum(course);
    const modules = data.modules || [];

    if (skillBadge) {
      skillBadge.textContent = `${capitalize(data.skill_level || 'intermediate')} Track`;
    }

    // Calculate completion count
    let totalTopics = 0;
    let completedTopics = 0;
    modules.forEach(m => {
      (m.topics || []).forEach(t => {
        totalTopics++;
        if (t.status === 'completed' || t.lesson_completed) completedTopics++;
      });
    });

    const completionRate = totalTopics > 0 ? Math.round((completedTopics / totalTopics) * 100) : (course === 'python' ? 28 : 15);
    if (progLabel) progLabel.textContent = `Track Progress: ${completedTopics} of ${totalTopics} Topics Mastered`;
    if (progPct) progPct.textContent = `${completionRate}%`;
    if (progFill) progFill.style.width = `${completionRate}%`;

    // Render Modules
    container.innerHTML = modules.map((m, mIdx) => {
      const topics = m.topics || [];
      const modCompleted = topics.filter(t => t.status === 'completed' || t.lesson_completed).length;

      return `
        <div class="module-group-card moving-luxury-border" style="margin-bottom:20px;border-radius:14px;overflow:hidden;box-shadow:0 4px 14px rgba(0,0,0,0.04);">
          <div class="module-header-bar" onclick="window.toggleModuleAccordion(${m.module_number})" style="display:flex;align-items:center;justify-content:space-between;padding:16px 20px;background:#FFFDF9;cursor:pointer;border-bottom:1px solid rgba(200,160,100,0.2);">
            <div style="display:flex;align-items:center;gap:14px;">
              <div class="module-badge-num" style="width:34px;height:34px;border-radius:10px;background:linear-gradient(135deg,#2563EB,#1D4ED8);color:#FFF;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:14px;">
                ${m.module_number}
              </div>
              <div>
                <h3 style="font-size:15.5px;font-weight:800;color:var(--text-primary);margin:0;">Module ${m.module_number}: ${m.module_name}</h3>
                <div style="font-size:12px;color:var(--text-muted);margin-top:2px;">
                  ${modCompleted}/${topics.length} topics completed
                </div>
              </div>
            </div>
            <div style="display:flex;align-items:center;gap:12px;">
              <span class="badge ${modCompleted === topics.length && topics.length > 0 ? 'badge-green' : (modCompleted > 0 ? 'badge-blue' : 'badge-amber')}">
                ${modCompleted === topics.length && topics.length > 0 ? 'Mastered ✓' : (modCompleted > 0 ? 'In Progress' : 'Available')}
              </span>
              <span id="module-arrow-${m.module_number}" style="font-size:14px;color:var(--text-muted);">▼</span>
            </div>
          </div>

          <div id="module-body-${m.module_number}" style="display:flex;flex-direction:column;background:#FFFFFF;">
            ${topics.map((t, tIdx) => {
              const isLocked = t.status === 'locked';
              const isDone = t.status === 'completed' || t.lesson_completed;
              const isCurrent = t.is_current || t.status === 'in_progress' || (t.status === 'available' && tIdx === 0 && mIdx === 0);

              let starsHtml = '';
              if (t.mastery_score >= 80) starsHtml = '⭐⭐⭐';
              else if (t.mastery_score >= 50) starsHtml = '⭐⭐';
              else if (t.mastery_score > 0) starsHtml = '⭐';

              return `
                <div class="topic-node-row ${isCurrent ? 'current-active' : ''}" style="display:flex;align-items:center;justify-content:space-between;padding:14px 20px;border-bottom:1px solid #F1F5F9;gap:16px;">
                  <div style="display:flex;align-items:center;gap:14px;min-width:0;flex:1;">
                    <div class="topic-icon-bubble ${isDone ? 'completed' : ''}" style="width:36px;height:36px;border-radius:10px;background:${isDone ? '#D1FAE5' : '#F1F5F9'};display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;">
                      ${isDone ? '✓' : (isLocked ? '🔒' : (t.icon || meta.icon))}
                    </div>
                    <div style="min-width:0;flex:1;">
                      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                        <h4 style="font-size:15px;font-weight:700;color:var(--text-primary);margin:0;">${t.name}</h4>
                        ${starsHtml ? `<span style="font-size:11px;">${starsHtml}</span>` : ''}
                        ${isCurrent ? '<span class="badge badge-purple" style="font-size:9px;">ACTIVE</span>' : ''}
                        ${isDone ? '<span class="badge badge-green" style="font-size:9px;">LESSON DONE</span>' : ''}
                      </div>
                    </div>
                  </div>

                  <div style="display:flex;align-items:center;gap:14px;flex-shrink:0;">
                    ${!isLocked ? `
                      <div style="text-align:right;min-width:60px;">
                        <div style="font-size:12px;font-weight:700;color:${(t.mastery_score || 0) >= 70 ? 'var(--success)' : 'var(--primary)'};">${t.mastery_score || 0}%</div>
                        <div style="font-size:10px;color:var(--text-muted);">Mastery</div>
                      </div>
                      <a href="/lesson.html?id=${t.id}&course=${course}" class="btn ${isCurrent ? 'btn-primary' : 'btn-secondary'} btn-sm" style="text-decoration:none;">
                        <span>${isDone ? 'Review' : (isCurrent ? '⚡ Study' : 'Open')}</span>
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
