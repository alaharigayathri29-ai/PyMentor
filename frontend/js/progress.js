/**
 * progress.js
 * Student Progress Dashboard Controller (Real Multi-Page Application)
 * Calculates topic mastery, assessment history, accuracy, and streaks directly from database records.
 */

import { requireAuth, initLayout, renderEmptyState, escapeHtml } from './common.js?v=20261108_v17';
import { progressApi } from './api.js?v=20261108_v17';
import { capitalize, formatRelative, formatDate } from './utils/formatters.js?v=20261108_v17';

async function init() {
  const user = await requireAuth();
  if (!user) return;

  initLayout('progress', user);

  const tierBadge = document.getElementById('prog-skill-tier-badge');
  const diagnosticScore = document.getElementById('prog-diagnostic-score');
  const solvedCount = document.getElementById('prog-solved-count');
  const accuracyRate = document.getElementById('prog-accuracy-rate');
  const streakVal = document.getElementById('prog-streak-val');
  const completedTopicsStat = document.getElementById('prog-completed-topics-stat');
  const masteryContainer = document.getElementById('prog-mastery-cards-container');
  const submissionsLedger = document.getElementById('prog-submissions-ledger');

  try {
    const data = await progressApi.get();
    const gamify = data.gamification || {};

    // 1. Skill Tier & Diagnostic Score
    const skillLevel = data.skill_level && data.skill_level !== 'unassessed' ? capitalize(data.skill_level) : 'New Learner';
    if (tierBadge) {
      tierBadge.textContent = `${skillLevel} Track`;
      tierBadge.className = `badge ${skillLevel.toLowerCase().includes('adv') ? 'badge-amber' : skillLevel.toLowerCase().includes('inter') ? 'badge-teal' : 'badge-blue'}`;
    }

    if (diagnosticScore) {
      const diagAttempts = data.assessment_history || [];
      if (diagAttempts.length > 0) {
        diagnosticScore.textContent = `${Math.round(diagAttempts[0].score || 0)}%`;
      } else {
        diagnosticScore.textContent = `${Math.round(data.overall_progress || 0)}%`;
      }
    }

    // 2. Metrics Grid
    if (solvedCount) solvedCount.textContent = data.problems_solved || 0;
    if (accuracyRate) accuracyRate.textContent = `${Math.round(data.accuracy_pct || 0)}%`;
    if (streakVal) streakVal.textContent = `${gamify.streak_days || 0} Days`;
    if (completedTopicsStat) completedTopicsStat.textContent = `${data.completed_count || 0} / ${data.total_topics || 13}`;

    // 3. Topic-wise Mastery Grid
    if (masteryContainer) {
      const topics = data.topics || [];
      if (topics.length > 0) {
        masteryContainer.innerHTML = topics.map(t => {
          const score = Math.round(t.mastery_score || 0);
          const isDone = t.status === 'completed' || score >= 70;
          return `
            <div class="mastery-card" style="padding:16px;background:#FFFFFF;border:1px solid var(--border);border-radius:var(--r-lg);box-shadow:var(--shadow-xs);">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                <div style="display:flex;align-items:center;gap:8px;">
                  <span style="font-size:20px;">${t.icon || '📚'}</span>
                  <span style="font-size:14px;font-weight:700;color:var(--text-primary);">${escapeHtml(t.topic_name || t.name)}</span>
                </div>
                <span class="badge ${isDone ? 'badge-green' : (score > 0 ? 'badge-blue' : 'badge-gray')}" style="font-size:10px;">
                  ${isDone ? 'Mastered ✓' : (score > 0 ? 'In Progress' : 'Pending')}
                </span>
              </div>
              <div class="progress-bar-wrap" style="height:6px;margin-bottom:8px;">
                <div class="progress-bar-fill" style="width:${score}%;background-color:${isDone ? 'var(--success)' : 'var(--primary)'};"></div>
              </div>
              <div style="display:flex;justify-content:space-between;font-size:11.5px;color:var(--text-secondary);">
                <span>Mastery Rating</span>
                <span style="font-weight:700;color:var(--text-primary);">${score}%</span>
              </div>
            </div>
          `;
        }).join('');
      } else {
        renderEmptyState(masteryContainer, {
          icon: '📚',
          title: 'No topic metrics recorded',
          message: 'Complete lessons and practice problems to build your topic mastery ledger.',
          actionText: 'View Curriculum Roadmap',
          actionHref: '/learning-path.html',
        });
      }
    }

    // 4. Submissions Ledger Table
    if (submissionsLedger) {
      const subs = data.recent_submissions || [];
      if (subs.length > 0) {
        submissionsLedger.innerHTML = `
          <div style="overflow-x:auto;">
            <table class="data-table" style="width:100%;text-align:left;border-collapse:collapse;">
              <thead>
                <tr style="border-bottom:1px solid var(--border);color:var(--text-secondary);font-size:12px;text-transform:uppercase;">
                  <th style="padding:12px 16px;">Problem</th>
                  <th style="padding:12px 16px;">Difficulty</th>
                  <th style="padding:12px 16px;">Submitted</th>
                  <th style="padding:12px 16px;">Test Cases</th>
                  <th style="padding:12px 16px;text-align:right;">Score</th>
                </tr>
              </thead>
              <tbody>
                ${subs.map(s => `
                  <tr style="border-bottom:1px solid var(--border);font-size:13.5px;">
                    <td style="padding:14px 16px;font-weight:600;color:var(--text-primary);">${escapeHtml(s.problem_title)}</td>
                    <td style="padding:14px 16px;">
                      <span class="badge ${s.difficulty === 'easy' ? 'badge-beginner' : s.difficulty === 'medium' ? 'badge-intermediate' : 'badge-advanced'}" style="font-size:11px;">
                        ${capitalize(s.difficulty || 'easy')}
                      </span>
                    </td>
                    <td style="padding:14px 16px;color:var(--text-secondary);font-size:12.5px;">${formatRelative(s.submitted_at)}</td>
                    <td style="padding:14px 16px;color:var(--text-primary);font-family:var(--font-mono);font-size:12.5px;">${s.passed} / ${s.total} Passed</td>
                    <td style="padding:14px 16px;text-align:right;">
                      <span class="badge ${s.score >= 70 ? 'badge-green' : 'badge-red'}" style="font-size:12px;font-weight:700;">
                        ${Math.round(s.score)}%
                      </span>
                    </td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        `;
      } else {
        renderEmptyState(submissionsLedger, {
          icon: '📝',
          title: 'No Problem Submissions Recorded',
          message: 'You have not submitted any coding solutions yet. Solutions tested in the Practice Lab will appear here.',
          actionText: 'Solve a Problem →',
          actionHref: '/practice.html',
        });
      }
    }

  } catch (err) {
    console.error('[Progress] Error loading progress ledger:', err);
    if (masteryContainer) {
      renderEmptyState(masteryContainer, {
        icon: '⚠️',
        title: 'Unable to Load Progress Data',
        message: err.message,
      });
    }
  }
}

init();
