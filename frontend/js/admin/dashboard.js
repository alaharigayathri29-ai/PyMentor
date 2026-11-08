/**
 * admin/dashboard.js
 * Admin Overview Controller (Real Multi-Page Application)
 * Protected with strict requireAdmin check.
 */

import { requireAuth, initLayout, escapeHtml } from '../common.js?v=20261108_v17';
import { adminApi } from '../api.js?v=20261108_v17';
import { showToast } from '../components/toast.js?v=20261108_v17';
import { capitalize, formatRelative } from '../utils/formatters.js?v=20261108_v17';

async function init() {
  const user = await requireAuth({ requireAdmin: true });
  if (!user) return;

  initLayout('admin-dashboard', user);

  const totalStudents = document.getElementById('adm-total-students');
  const passRate = document.getElementById('adm-pass-rate');
  const avgQuiz = document.getElementById('adm-avg-quiz');
  const totalSubs = document.getElementById('adm-total-subs');
  const tierBars = document.getElementById('adm-tier-bars');
  const recentList = document.getElementById('adm-recent-students-list');
  const seedBtn = document.getElementById('btn-admin-seed-demo');
  const refreshBtn = document.getElementById('btn-admin-refresh');

  seedBtn?.addEventListener('click', async () => {
    try {
      seedBtn.disabled = true;
      seedBtn.innerHTML = '<span>Seeding…</span>';
      await adminApi.seedDemo();
      showToast('Demo students seeded successfully!', 'success');
      loadOverviewData();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      seedBtn.disabled = false;
      seedBtn.innerHTML = '<span>🌱 Seed 4 Demo Students</span>';
    }
  });

  refreshBtn?.addEventListener('click', () => {
    showToast('Refreshing metrics…', 'info');
    loadOverviewData();
  });

  async function loadOverviewData() {
    try {
      const [stats, users] = await Promise.all([
        adminApi.stats(),
        adminApi.users(),
      ]);

      if (totalStudents) totalStudents.textContent = `${stats.total_students || 0} (${stats.active_students || 0} Active)`;
      if (passRate) passRate.textContent = `${stats.submission_pass_rate || 0}%`;
      if (avgQuiz) avgQuiz.textContent = `${stats.average_assessment_score || 0}%`;
      if (totalSubs) totalSubs.textContent = stats.total_submissions || 0;

      // Skill distribution
      if (tierBars) {
        const dist = stats.skill_level_distribution || {};
        const total = Object.values(dist).reduce((a, b) => a + b, 0) || 1;
        const tiers = [
          { key: 'beginner', color: 'var(--green)' },
          { key: 'intermediate', color: 'var(--amber)' },
          { key: 'advanced', color: 'var(--purple)' },
        ];

        tierBars.innerHTML = tiers.map(t => {
          const count = dist[t.key] || 0;
          const pct = Math.round((count / total) * 100);
          return `
            <div style="margin-bottom:12px;">
              <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px;">
                <span style="color:var(--text-primary);font-weight:600;">${capitalize(t.key)}</span>
                <span style="color:var(--text-secondary);">${count} students (${pct}%)</span>
              </div>
              <div class="progress-bar-wrap" style="height:8px;">
                <div class="progress-bar-fill" style="width:${pct}%;background:${t.color};"></div>
              </div>
            </div>
          `;
        }).join('');
      }

      // Recent registered students
      if (recentList) {
        if (users && users.length > 0) {
          recentList.innerHTML = users.slice(0, 5).map(u => `
            <div style="padding:12px 14px;background:#F8FAFC;border:1px solid var(--border);border-radius:var(--r-md);display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
              <div>
                <div style="font-weight:600;font-size:13.5px;color:var(--text-primary);">${escapeHtml(u.username)}</div>
                <div style="font-size:11px;color:var(--text-secondary);">${escapeHtml(u.email)} • Active ${formatRelative(u.last_active)}</div>
              </div>
              <div style="display:flex;align-items:center;gap:10px;">
                <span class="badge ${u.skill_level === 'beginner' ? 'badge-beginner' : (u.skill_level === 'intermediate' ? 'badge-intermediate' : 'badge-advanced')}">
                  ${capitalize(u.skill_level || 'unassessed')}
                </span>
                <a href="/admin/students.html" class="btn btn-ghost btn-sm" style="font-size:11px;text-decoration:none;">Inspect →</a>
              </div>
            </div>
          `).join('');
        } else {
          recentList.innerHTML = '<div style="padding:20px;text-align:center;color:var(--text-muted);font-size:13px;">No registered students found.</div>';
        }
      }

    } catch (err) {
      console.error('[Admin Dashboard] Error:', err);
    }
  }

  loadOverviewData();
}

init();

