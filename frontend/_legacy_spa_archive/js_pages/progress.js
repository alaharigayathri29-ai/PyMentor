/**
 * Student Progress Dashboard Controller.
 * Real DB metrics: topic-wise mastery, assessment history, accuracy, and strong/weak topics.
 */

import { progressApi } from '../api.js';
import { capitalize, formatRelative, formatDate } from '../utils/formatters.js';

export async function initProgress() {
  const overallPct = document.getElementById('prog-overall-pct');
  const accuracyPct = document.getElementById('prog-accuracy-pct');
  const solvedCount = document.getElementById('prog-solved-count');
  const streakVal = document.getElementById('prog-streak-val');
  const strongList = document.getElementById('prog-strong-list');
  const weakList = document.getElementById('prog-weak-list');
  const topicsGrid = document.getElementById('prog-topics-grid');
  const subsTable = document.getElementById('prog-subs-table');
  const assessTable = document.getElementById('prog-assessment-table');

  try {
    const data = await progressApi.get();
    const gamify = data.gamification || {};

    if (overallPct) overallPct.textContent = `${data.overall_progress || 0}%`;
    if (accuracyPct) accuracyPct.textContent = `${data.accuracy_pct || 0}%`;
    if (solvedCount) solvedCount.textContent = `${data.problems_solved || 0}`;
    if (streakVal) streakVal.textContent = `${gamify.streak_days || 0} Days`;

    // Strong topics
    if (strongList) {
      const strong = data.strong_topics || [];
      if (strong.length > 0) {
        strongList.innerHTML = strong.map(s => `
          <span class="badge badge-green" style="font-size:12px;padding:4px 10px;">✓ ${escapeHtml(s)}</span>
        `).join('');
      } else {
        strongList.innerHTML = '<span style="font-size:12px;color:var(--text-muted);">Reach 70%+ mastery on any topic to add to your strengths!</span>';
      }
    }

    // Weak topics
    if (weakList) {
      const weak = data.weak_topics || [];
      if (weak.length > 0) {
        weakList.innerHTML = weak.map(w => `
          <span class="badge badge-amber" style="font-size:12px;padding:4px 10px;">⚠️ ${escapeHtml(w)}</span>
        `).join('');
      } else {
        weakList.innerHTML = '<span style="font-size:12px;color:#6ee7b7;">✓ No topics requiring review right now!</span>';
      }
    }

    // Topic-wise mastery grid
    if (topicsGrid) {
      const topics = data.topics || [];
      topicsGrid.innerHTML = topics.map(t => {
        const isMastered = t.mastery_score >= 70;
        return `
          <div style="padding:14px;background:rgba(255,255,255,0.02);border:1px solid var(--border);border-radius:10px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
              <span style="font-weight:700;font-size:13.5px;color:#fff;">${t.icon || '📚'} ${escapeHtml(t.topic_name)}</span>
              <span class="badge ${isMastered ? 'badge-green' : (t.mastery_score > 0 ? 'badge-purple' : 'badge-gray')}">
                ${t.mastery_score}%
              </span>
            </div>
            <div class="progress-bar-wrap" style="height:6px;margin-bottom:6px;">
              <div class="progress-bar-fill" style="width:${Math.min(100, t.mastery_score)}%;background:${isMastered ? 'var(--green)' : 'var(--purple)'};"></div>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:11px;color:var(--text-muted);">
              <span>${capitalize(t.difficulty || 'beginner')}</span>
              <span>${t.attempts || 0} attempts</span>
            </div>
          </div>
        `;
      }).join('');
    }

    // Recent practice submissions table
    if (subsTable) {
      const subs = data.recent_submissions || [];
      if (subs.length > 0) {
        subsTable.innerHTML = subs.map(s => `
          <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 14px;background:rgba(255,255,255,0.02);border:1px solid var(--border);border-radius:8px;">
            <div>
              <div style="font-weight:600;font-size:13px;color:#fff;">${escapeHtml(s.problem_title)}</div>
              <div style="font-size:11px;color:var(--text-muted);">${formatRelative(s.submitted_at)} • ${capitalize(s.difficulty)}</div>
            </div>
            <div style="text-align:right;">
              <span class="badge ${s.score >= 70 ? 'badge-green' : 'badge-red'}">
                ${s.passed}/${s.total} (${Math.round(s.score)}%)
              </span>
            </div>
          </div>
        `).join('');
      } else {
        subsTable.innerHTML = '<div style="font-size:12px;color:var(--text-muted);padding:8px 0;">No coding submissions recorded yet.</div>';
      }
    }

    // Assessment attempts table
    if (assessTable) {
      const attempts = data.assessment_history || [];
      if (attempts.length > 0) {
        assessTable.innerHTML = attempts.map(a => `
          <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 14px;background:rgba(255,255,255,0.02);border:1px solid var(--border);border-radius:8px;">
            <div>
              <div style="font-weight:600;font-size:13px;color:#fff;">Diagnostic Quiz</div>
              <div style="font-size:11px;color:var(--text-muted);">${formatDate(a.completed_at)}</div>
            </div>
            <div style="text-align:right;">
              <span class="badge badge-purple">${capitalize(a.skill_level || 'beginner')} (${Math.round(a.score || 0)}%)</span>
            </div>
          </div>
        `).join('');
      } else {
        assessTable.innerHTML = '<div style="font-size:12px;color:var(--text-muted);padding:8px 0;">No assessment attempts recorded yet.</div>';
      }
    }

  } catch (err) {
    console.warn('[Progress] Load error:', err);
  }
}

function escapeHtml(str) {
  return (str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

