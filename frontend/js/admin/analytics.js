/**
 * admin/analytics.js
 * Platform Analytics & Intelligence Controller (Real Multi-Page Application)
 */

import { requireAuth, initLayout, escapeHtml } from '../common.js?v=20261108_v17';
import { adminApi } from '../api.js?v=20261108_v17';
import { showToast } from '../components/toast.js?v=20261108_v17';
import { capitalize } from '../utils/formatters.js?v=20261108_v17';

async function init() {
  const user = await requireAuth({ requireAdmin: true });
  if (!user) return;

  initLayout('admin-analytics', user);

  await loadAnalytics();

  document.getElementById('btn-refresh-analytics')?.addEventListener('click', async () => {
    showToast('Refreshing platform intelligence…', 'info');
    await loadAnalytics();
  });
}

async function loadAnalytics() {
  try {
    const [stats, users, content] = await Promise.all([
      adminApi.stats(),
      adminApi.users(),
      adminApi.getContentItems(),
    ]);

    renderKPIs(stats);
    renderSkillDistribution(stats);
    renderContentMetrics(content, stats);
    renderTopLearners(users);
  } catch (err) {
    showToast(`Failed to load analytics: ${err.message}`, 'error');
  }
}

function renderKPIs(stats) {
  const total = stats.total_students || 0;
  const active = stats.active_students || 0;
  const activeRate = total > 0 ? Math.round((active / total) * 100) : 0;

  const elTotal = document.getElementById('stat-total-students');
  const elActiveRate = document.getElementById('stat-active-rate');
  const elPassRate = document.getElementById('stat-pass-rate');
  const elAvgScore = document.getElementById('stat-avg-score');
  const elAvgSub = document.getElementById('stat-avg-sub');
  const elAiSessions = document.getElementById('stat-ai-sessions');

  if (elTotal) elTotal.textContent = total;
  if (elActiveRate) elActiveRate.textContent = `${activeRate}% (${active} active)`;
  if (elPassRate) elPassRate.textContent = `${stats.submission_pass_rate || 0}%`;
  if (elAvgScore) elAvgScore.textContent = `${stats.average_assessment_score || 0}%`;
  if (elAvgSub) elAvgSub.textContent = `${stats.average_submission_score || 0}%`;
  if (elAiSessions) elAiSessions.textContent = stats.total_mentor_sessions || 0;
}

function renderSkillDistribution(stats) {
  const dist = stats.skill_level_distribution || {};
  const total = stats.total_students || 0;

  const bCount = dist['beginner'] || 0;
  const iCount = dist['intermediate'] || 0;
  const aCount = dist['advanced'] || 0;
  const unassessed = Math.max(0, total - (bCount + iCount + aCount));

  const bPct = total > 0 ? Math.round((bCount / total) * 100) : 0;
  const iPct = total > 0 ? Math.round((iCount / total) * 100) : 0;
  const aPct = total > 0 ? Math.round((aCount / total) * 100) : 0;
  const uPct = total > 0 ? Math.round((unassessed / total) * 100) : 0;

  const container = document.getElementById('skill-distribution-container');
  if (!container) return;

  container.innerHTML = `
    <div style="display:flex;flex-direction:column;gap:16px;">
      <div>
        <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px;">
          <span style="font-weight:600;color:var(--green);">🌱 Beginner</span>
          <span style="color:var(--text-muted);">${bCount} students (${bPct}%)</span>
        </div>
        <div class="progress-bar-wrap" style="height:8px;background:var(--bg-elevated);border-radius:4px;overflow:hidden;">
          <div style="height:100%;width:${bPct}%;background:var(--green);border-radius:4px;transition:width 0.4s ease;"></div>
        </div>
      </div>

      <div>
        <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px;">
          <span style="font-weight:600;color:var(--blue);">⚡ Intermediate</span>
          <span style="color:var(--text-muted);">${iCount} students (${iPct}%)</span>
        </div>
        <div class="progress-bar-wrap" style="height:8px;background:var(--bg-elevated);border-radius:4px;overflow:hidden;">
          <div style="height:100%;width:${iPct}%;background:var(--blue);border-radius:4px;transition:width 0.4s ease;"></div>
        </div>
      </div>

      <div>
        <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px;">
          <span style="font-weight:600;color:var(--purple);">🚀 Advanced</span>
          <span style="color:var(--text-muted);">${aCount} students (${aPct}%)</span>
        </div>
        <div class="progress-bar-wrap" style="height:8px;background:var(--bg-elevated);border-radius:4px;overflow:hidden;">
          <div style="height:100%;width:${aPct}%;background:var(--purple);border-radius:4px;transition:width 0.4s ease;"></div>
        </div>
      </div>

      <div>
        <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px;">
          <span style="font-weight:600;color:var(--text-muted);">❓ Unassessed / New</span>
          <span style="color:var(--text-muted);">${unassessed} students (${uPct}%)</span>
        </div>
        <div class="progress-bar-wrap" style="height:8px;background:var(--bg-elevated);border-radius:4px;overflow:hidden;">
          <div style="height:100%;width:${uPct}%;background:var(--text-muted);border-radius:4px;transition:width 0.4s ease;"></div>
        </div>
      </div>
    </div>
  `;
}

function renderContentMetrics(content, stats) {
  const elTopics = document.getElementById('stat-total-topics');
  const elProblems = document.getElementById('stat-total-problems');
  const elQuestions = document.getElementById('stat-total-questions');
  const elSubmissions = document.getElementById('stat-total-submissions');

  if (elTopics) elTopics.textContent = (content.topics || []).length;
  if (elProblems) elProblems.textContent = (content.problems || []).length;
  if (elQuestions) elQuestions.textContent = (content.questions || []).length;
  if (elSubmissions) elSubmissions.textContent = stats.total_submissions || 0;
}

function renderTopLearners(users) {
  const container = document.getElementById('top-learners-container');
  if (!container) return;

  if (!users || users.length === 0) {
    container.innerHTML = '<div style="padding:24px;text-align:center;color:var(--text-muted);font-size:13px;">No student activity recorded yet.</div>';
    return;
  }

  // Sort by submissions count descending, then avg_submission_score
  const sorted = [...users].sort((a, b) => {
    if (b.submission_count !== a.submission_count) {
      return b.submission_count - a.submission_count;
    }
    return b.avg_submission_score - a.avg_submission_score;
  }).slice(0, 5);

  container.innerHTML = `
    <table class="admin-table">
      <thead>
        <tr>
          <th>Learner</th>
          <th>Skill Level</th>
          <th>Submissions</th>
          <th>Avg Code Score</th>
          <th>Assessment</th>
          <th style="text-align:right;">Actions</th>
        </tr>
      </thead>
      <tbody>
        ${sorted.map(u => `
          <tr>
            <td>
              <div style="font-weight:600;color:var(--text-primary);font-size:13px;">${escapeHtml(u.username)}</div>
              <div style="font-size:11px;color:var(--text-secondary);">${escapeHtml(u.email)}</div>
            </td>
            <td>
              <span class="badge ${u.skill_level === 'beginner' ? 'badge-beginner' : u.skill_level === 'intermediate' ? 'badge-intermediate' : u.skill_level === 'advanced' ? 'badge-advanced' : 'badge-ghost'}">
                ${u.skill_level ? capitalize(u.skill_level) : 'Unassessed'}
              </span>
            </td>
            <td>
              <span style="font-weight:600;color:var(--text-primary);">${u.submission_count}</span>
            </td>
            <td>
              <span style="font-weight:600;color:${u.avg_submission_score >= 70 ? 'var(--green)' : 'var(--text-secondary)'};">
                ${u.avg_submission_score}%
              </span>
            </td>
            <td>
              ${u.assessment_score !== null ? `<span style="font-weight:600;color:var(--text-accent);">${u.assessment_score}%</span>` : '<span style="color:var(--text-muted);font-size:12px;">Pending</span>'}
            </td>
            <td style="text-align:right;">
              <a href="/admin/student-details.html?id=${u.id}" class="btn btn-ghost btn-sm" style="font-size:11px;text-decoration:none;">Inspect →</a>
            </td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;
}

init();
