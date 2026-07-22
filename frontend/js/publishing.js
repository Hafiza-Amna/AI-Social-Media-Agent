/**
 * publishing.js — Publishing Queue & Management Center Controller
 */

class PublishingCenterController {
  constructor() {
    this.currentFilter = null;
  }

  async init() {
    await this.refreshData();
  }

  async setFilter(status) {
    this.currentFilter = status;
    
    // Update filter button UI states
    document.querySelectorAll(".pub-filter-btn").forEach(btn => {
      btn.classList.remove("btn-primary");
      btn.classList.add("btn-secondary");
    });
    const activeBtn = document.getElementById(`filter-btn-${status || 'all'}`);
    if (activeBtn) {
      activeBtn.classList.remove("btn-secondary");
      activeBtn.classList.add("btn-primary");
    }

    await this.refreshData();
  }

  async refreshData() {
    const tableBody = document.getElementById("publishing-queue-tbody");
    if (!tableBody) return;

    try {
      tableBody.innerHTML = `
        <tr>
          <td colspan="6" class="empty-state">
            <span class="spinner"></span>
            <p style="margin-top: 8px;">Loading publishing queue...</p>
          </td>
        </tr>
      `;

      const data = await window.api.getJobs(this.currentFilter);
      const jobs = data.jobs || [];

      if (jobs.length === 0) {
        tableBody.innerHTML = `
          <tr>
            <td colspan="6" class="empty-state">
              <i class="ri-inbox-archive-line"></i>
              <h4>No Jobs Found</h4>
              <p>No publishing jobs match the selected status filter.</p>
            </td>
          </tr>
        `;
        return;
      }

      let html = "";
      jobs.forEach(job => {
        const dateStr = new Date(job.created_at || Date.now()).toLocaleString();
        const platform = job.platform || "LinkedIn";
        const platformClass = platform.toLowerCase();
        const statusClass = `badge-${job.status.toLowerCase()}`;
        const snippet = job.content ? (job.content.length > 50 ? job.content.substring(0, 50) + "..." : job.content) : "No Content";

        let actionBtn = "";
        if (job.status === "approved") {
          actionBtn = `<button class="btn btn-sm btn-primary" onclick="window.publishingController.executeJob('${job.job_id}')"><i class="ri-play-fill"></i> Execute</button>`;
        } else if (job.status === "pending_review") {
          actionBtn = `<button class="btn btn-sm btn-secondary" onclick="window.app.switchTab('approval')"><i class="ri-search-line"></i> Review</button>`;
        } else if (job.publication_id) {
          actionBtn = `<span style="font-size: 11px; color: var(--text-dim);" title="${job.publication_id}">${job.publication_id.substring(0, 16)}...</span>`;
        } else {
          actionBtn = `-`;
        }

        html += `
          <tr>
            <td><code>${job.job_id}</code></td>
            <td>
              <span class="platform-badge ${platformClass}">
                <i class="ri-${platformClass}-fill"></i> ${platform}
              </span>
            </td>
            <td title="${job.content}">${snippet}</td>
            <td><span class="badge ${statusClass}">${job.status.replace('_', ' ')}</span></td>
            <td style="font-size: 12px; color: var(--text-muted);">${dateStr}</td>
            <td>${actionBtn}</td>
          </tr>
        `;
      });

      tableBody.innerHTML = html;

    } catch (error) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="6" class="empty-state">
            <i class="ri-error-warning-line" style="color: var(--danger);"></i>
            <h4>Error Loading Queue</h4>
            <p>${error.message}</p>
          </td>
        </tr>
      `;
    }
  }

  async executeJob(jobId) {
    try {
      window.app.showToast("Executing job publishing...", "info");
      const res = await window.api.executeJob(jobId);
      
      if (res.success) {
        window.app.showToast("Job executed and published successfully!", "success");
      } else {
        window.app.showToast(`Execution failed: ${res.message}`, "error");
      }

      await this.refreshData();
      if (window.dashboardController) window.dashboardController.refreshData();
    } catch (error) {
      window.app.showToast(`Execute failed: ${error.message}`, "error");
    }
  }
}

window.publishingController = new PublishingCenterController();
