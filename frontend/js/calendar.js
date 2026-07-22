/**
 * calendar.js — Content Calendar & Schedule View Controller
 */

class ContentCalendarController {
  async init() {
    await this.refreshData();
  }

  async refreshData() {
    const container = document.getElementById("calendar-posts-container");
    if (!container) return;

    try {
      const data = await window.api.getJobs();
      const jobs = data.jobs || [];

      if (jobs.length === 0) {
        container.innerHTML = `
          <div class="empty-state">
            <i class="ri-calendar-event-line"></i>
            <h4>No Posts Scheduled</h4>
            <p>Use the AI Content Generator to generate and queue posts.</p>
          </div>
        `;
        return;
      }

      let html = '<div style="display: grid; gap: 16px;">';
      jobs.forEach(job => {
        const scheduledTime = job.scheduled_datetime 
          ? new Date(job.scheduled_datetime).toLocaleString() 
          : new Date(job.created_at || Date.now()).toLocaleString();

        const platform = job.platform || "LinkedIn";
        const platformClass = platform.toLowerCase();
        const statusClass = `badge-${job.status.toLowerCase()}`;

        html += `
          <div class="card" style="margin-bottom: 0; padding: 18px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
              <div style="display: flex; align-items: center; gap: 12px;">
                <span class="platform-badge ${platformClass}">
                  <i class="ri-${platformClass}-fill"></i> ${platform}
                </span>
                <span class="badge ${statusClass}">${job.status.replace('_', ' ')}</span>
              </div>
              <div style="font-size: 13px; font-weight: 600; color: var(--primary);">
                <i class="ri-time-line"></i> ${scheduledTime}
              </div>
            </div>
            <div style="font-size: 14px; color: var(--text-main); line-height: 1.5; background-color: var(--bg-input); padding: 12px; border-radius: var(--radius-sm); border: 1px solid var(--border-color);">
              ${job.content ? (job.content.length > 160 ? job.content.substring(0, 160) + '...' : job.content) : 'No content'}
            </div>
          </div>
        `;
      });
      html += '</div>';
      container.innerHTML = html;

    } catch (error) {
      container.innerHTML = `
        <div class="empty-state">
          <i class="ri-error-warning-line" style="color: var(--danger);"></i>
          <h4>Error Loading Calendar</h4>
          <p>${error.message}</p>
        </div>
      `;
    }
  }
}

window.calendarController = new ContentCalendarController();
