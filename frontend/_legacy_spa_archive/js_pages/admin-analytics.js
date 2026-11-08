/**
 * admin-analytics.js
 * Platform Analytics & Aggregate Learning Metrics
 */
import { adminApi } from '../api.js';
import { toast } from '../components/toast.js';

export async function initAdminAnalytics() {
  document.getElementById('btn-refresh-analytics')?.addEventListener('click', loadAnalytics);
  await loadAnalytics();
}

async function loadAnalytics() {
  try {
    const stats = await adminApi.stats();

    // Pass Rate
    const passRateEl = document.getElementById('analytics-pass-rate');
    const passBarEl = document.getElementById('analytics-pass-bar');
    if (passRateEl) passRateEl.textContent = `${stats.submission_pass_rate || 0}%`;
    if (passBarEl) passBarEl.style.width = `${Math.min(stats.submission_pass_rate || 0, 100)}%`;

    // AI Sessions
    const sessionsEl = document.getElementById('analytics-sessions-total');
    if (sessionsEl) sessionsEl.textContent = stats.total_mentor_sessions || 0;

    // Vitals Grid
    const vitalsGrid = document.getElementById('analytics-vitals-grid');
    if (vitalsGrid) {
      const vitals = [
        { label: 'Total Registered Students', val: stats.total_students, color: 'var(--text-accent)' },
        { label: 'Active Student Accounts', val: stats.active_students, color: 'var(--green)' },
        { label: 'Diagnostic Assessments Completed', val: stats.total_assessments, color: 'var(--blue)' },
        { label: 'Coding Practice Submissions', val: stats.total_submissions, color: 'var(--purple)' },
        { label: 'Average Diagnostic Score', val: `${stats.average_assessment_score}%`, color: 'var(--amber)' },
        { label: 'Average Practice Score', val: `${stats.average_submission_score}%`, color: 'var(--cyan)' },
      ];

      vitalsGrid.innerHTML = vitals.map(v => `
        <div style="background:var(--bg-elevated);border:1px solid var(--border);border-radius:var(--radius-md);padding:16px 20px;">
          <div style="font-size:12px;color:var(--text-muted);margin-bottom:6px;">${v.label}</div>
          <div style="font-size:26px;font-weight:700;color:${v.color};">${v.val}</div>
        </div>
      `).join('');
    }

  } catch (err) {
    toast.error('Failed to load platform analytics: ' + err.message);
  }
}

