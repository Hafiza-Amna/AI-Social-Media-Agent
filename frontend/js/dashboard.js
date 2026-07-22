/**
 * dashboard.js — Overview Dashboard Section Controller
 */

class DashboardController {
  async init() {
    await this.refreshData();
  }

  async refreshData() {
    try {
      const data = await window.api.getJobs();
      const jobs = data.jobs || [];

      // Calculate stat counts
      const total = jobs.length;
      const pending = jobs.filter(j => j.status === "pending_review").length;
      const scheduled = jobs.filter(j => j.status === "approved" || j.status === "scheduled").length;
      const published = jobs.filter(j => j.status === "published" || j.status === "Published").length;
      const failed = jobs.filter(j => j.status === "failed" || j.status === "Failed").length;

      // Update stat cards DOM
      document.getElementById("stat-total-posts").textContent = total;
      document.getElementById("stat-pending-posts").textContent = pending;
      document.getElementById("stat-scheduled-posts").textContent = scheduled;
      document.getElementById("stat-published-posts").textContent = published;
      document.getElementById("stat-failed-posts").textContent = failed;

      // Render recent activity list
      this.renderRecentActivity(jobs.slice(0, 5));
    } catch (error) {
      console.error("Dashboard refresh error:", error);
    }
  }

  renderRecentActivity(recentJobs) {
    const container = document.getElementById("recent-activity-list");
    if (!container) return;

    if (recentJobs.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <i class="ri-inbox-line"></i>
          <h4>No Activity Yet</h4>
          <p>Generate posts using the AI Content Generator to see activity here.</p>
        </div>
      `;
      return;
    }

    let html = '<div class="activity-timeline">';
    recentJobs.forEach(job => {
      const dateStr = new Date(job.created_at || Date.now()).toLocaleString();
      const statusClass = `badge-${job.status.toLowerCase()}`;
      const platformIcon = job.platform === "LinkedIn" ? "ri-linkedin-box-fill" : "ri-instagram-fill";

      html += `
        <div style="padding: 12px; border-bottom: 1px solid var(--border-color); display: flex; align-items: center; justify-content: space-between;">
          <div style="display: flex; align-items: center; gap: 12px;">
            <i class="${platformIcon} platform-badge ${job.platform ? job.platform.toLowerCase() : ''}" style="font-size: 20px;"></i>
            <div>
              <div style="font-weight: 600; font-size: 14px; color: var(--text-main);">
                ${job.content ? (job.content.substring(0, 55) + '...') : 'Social Media Post'}
              </div>
              <div style="font-size: 11px; color: var(--text-muted);">${dateStr}</div>
            </div>
          </div>
          <span class="badge ${statusClass}">${job.status.replace('_', ' ')}</span>
        </div>
      `;
    });
    html += '</div>';
    container.innerHTML = html;
  }
}

window.dashboardController = new DashboardController();
