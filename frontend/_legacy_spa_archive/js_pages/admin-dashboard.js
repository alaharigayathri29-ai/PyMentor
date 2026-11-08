/**
 * Admin Dashboard Controller (Overview).
 */

import { adminApi } from '../api.js';
import { showToast } from '../components/toast.js';
import { capitalize, formatRelative } from '../utils/formatters.js';

export async function initAdminDashboard() {
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
      initAdminDashboard();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      seedBtn.disabled = false;
      seedBtn.innerHTML = '<span>🌱 Seed 4 Demo Students</span>';
    }
  });

  refreshBtn?.addEventListener('click', () => {
    showToast('Refreshing metrics…', 'info');
    initAdminDashboard();
  });

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
          <div>
            <div style="display:flex;justify-content:space-between;font-size:12.5px;margin-bottom:6px;">
              <span style="font-weight:600;color:#fff;">${capitalize(t.key)}</span>
              <span style="color:${t.color};font-weight:700;">${count} Students (${pct}%)</span>
            </div>
            <div class="progress-bar-wrap" style="height:8px;">
              <div class="progress-bar-fill" style="width:${pct}%;background:${t.color};"></div>
            </div>
          </div>
        `;
      }).join('');
    }

    // Recent students
    if (recentList && users && users.length > 0) {
      recentList.innerHTML = users.slice(0, 5).map(u => `
        <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 14px;background:rgba(255,255,255,0.02);border:1px solid var(--border);border-radius:8px;">
          <div>
            <div style="font-weight:600;font-size:13px;color:#fff;">${escapeHtml(u.username)}</div>
            <div style="font-size:11px;color:var(--text-muted);">${escapeHtml(u.email)} • ${capitalize(u.skill_level || 'unassessed')}</div>
          </div>
          <div style="text-align:right;">
            <span class="badge ${u.is_active ? 'badge-green' : 'badge-red'}">${u.is_active ? 'Active' : 'Disabled'}</span>
          </div>
        </div>
      `).join('');
    }

  } catch (err) {
    console.warn('[AdminDashboard] Load error:', err);
  }
}

function escapeHtml(str) {
  return (str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

