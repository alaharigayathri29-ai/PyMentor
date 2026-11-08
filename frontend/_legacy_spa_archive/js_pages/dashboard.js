/**
 * Student Dashboard Controller.
 */

import { progressApi } from '../api.js';
import { capitalize, formatRelative } from '../utils/formatters.js';

export async function initDashboard() {
  const nameEl = document.getElementById('dash-student-name');
  const levelEl = document.getElementById('dash-level-val');
  const progressPctEl = document.getElementById('dash-progress-pct');
  const completedEl = document.getElementById('dash-completed-val');
  const solvedEl = document.getElementById('dash-solved-val');
  const ringPct = document.getElementById('dash-ring-pct');
  const ringSub = document.getElementById('dash-ring-sub');
  const svgRing = document.getElementById('dash-svg-ring');
  const streakPill = document.getElementById('dash-streak-pill');
  const rankBadge = document.getElementById('dash-rank-badge');
  const xpVal = document.getElementById('dash-xp-val');
  const focusTitle = document.getElementById('dash-focus-title');
  const focusDesc = document.getElementById('dash-focus-desc');
  const focusIcon = document.getElementById('dash-focus-icon');
  const recentList = document.getElementById('dash-recent-list');

  try {
    const data = await progressApi.get();
    const gamify = data.gamification || {};

    if (nameEl && window.currentUser) {
      nameEl.textContent = window.currentUser.username;
    }

    if (levelEl) levelEl.textContent = data.skill_level ? capitalize(data.skill_level) : 'Diagnostic Needed';
    if (progressPctEl) progressPctEl.textContent = `${data.overall_progress || 0}%`;
    if (completedEl) completedEl.textContent = `${data.completed_count || 0}/${data.total_topics || 14}`;
    if (solvedEl) solvedEl.textContent = data.problems_solved || 0;

    if (streakPill) streakPill.textContent = `🔥 ${gamify.streak_days || 0}-Day Streak`;
    if (rankBadge) rankBadge.textContent = `🎖️ Rank: ${gamify.level_rank || 'Apprentice'}`;
    if (xpVal) xpVal.textContent = `${gamify.xp || 0} XP`;

    // Circular progress ring calculation (circumference = 2 * PI * 42 ≈ 264)
    if (ringPct) ringPct.textContent = `${Math.round(data.overall_progress || 0)}%`;
    if (ringSub) ringSub.textContent = `${data.completed_count || 0} of ${data.total_topics || 14} topics mastered`;
    if (svgRing) {
      const pct = Math.min(100, Math.max(0, data.overall_progress || 0));
      const offset = 264 - (264 * pct / 100);
      svgRing.style.strokeDashoffset = offset;
    }

    // Current Focus / Recommended Next Topic
    if (data.current_topic && focusTitle) {
      focusTitle.textContent = data.current_topic;
      if (focusDesc) focusDesc.textContent = 'Continue your active study topic and complete its practice problems.';
    } else if (data.recommended_next && focusTitle) {
      focusTitle.textContent = data.recommended_next;
      if (focusDesc) focusDesc.textContent = 'Recommended next topic to advance your skill tier.';
    }

    // Recent activity
    if (recentList && data.recent_submissions && data.recent_submissions.length > 0) {
      recentList.innerHTML = data.recent_submissions.slice(0, 4).map(sub => `
        <div class="activity-item">
          <div>
            <div style="font-size:13px;font-weight:600;color:#fff;">${sub.problem_title}</div>
            <div style="font-size:11px;color:var(--text-muted);">${formatRelative(sub.submitted_at)} • ${capitalize(sub.difficulty)}</div>
          </div>
          <div style="text-align:right;">
            <span class="badge ${sub.score >= 70 ? 'badge-green' : 'badge-red'}">${sub.passed}/${sub.total} Passed (${Math.round(sub.score)}%)</span>
          </div>
        </div>
      `).join('');
    }

  } catch (err) {
    console.warn('[Dashboard] Data load error:', err);
  }
}

