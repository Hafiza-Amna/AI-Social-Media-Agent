/**
 * approval.js — Human-in-the-Loop Content Approval Center Controller
 */

class ApprovalCenterController {
  async init() {
    await this.refreshData();
  }

  async refreshData() {
    const container = document.getElementById("approval-cards-container");
    if (!container) return;

    try {
      container.innerHTML = `
        <div class="empty-state">
          <span class="spinner"></span>
          <p style="margin-top: 10px;">Loading pending approvals...</p>
        </div>
      `;

      const data = await window.api.getJobs("pending_review");
      const jobs = data.jobs || [];

      if (jobs.length === 0) {
        container.innerHTML = `
          <div class="empty-state">
            <i class="ri-checkbox-circle-line" style="color: var(--success);"></i>
            <h4>All Clear! No Pending Approvals</h4>
            <p>All posts have been reviewed or auto-published.</p>
          </div>
        `;
        return;
      }

      let html = '<div style="display: grid; gap: 20px;">';
      jobs.forEach(job => {
        const dateStr = new Date(job.created_at || Date.now()).toLocaleString();
        const platform = job.platform || "LinkedIn";
        const platformClass = platform.toLowerCase();

        html += `
          <div class="card" style="margin-bottom: 0;">
            <div class="card-header">
              <div style="display: flex; align-items: center; gap: 10px;">
                <span class="platform-badge ${platformClass}">
                  <i class="ri-${platformClass}-fill" style="font-size: 18px;"></i> ${platform}
                </span>
                <span class="badge badge-pending">Pending Human Review</span>
              </div>
              <span style="font-size: 12px; color: var(--text-dim);">Job ID: <code>${job.job_id}</code></span>
            </div>
            <div style="font-size: 14px; line-height: 1.6; color: var(--text-main); margin-bottom: 16px; background-color: var(--bg-input); padding: 14px; border-radius: var(--radius-md); border: 1px solid var(--border-color); white-space: pre-wrap;">${this.escapeHtml(job.content)}</div>
            
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
              <span style="font-size: 12px; color: var(--text-muted);"><i class="ri-time-line"></i> Queued: ${dateStr}</span>
              <div style="display: flex; gap: 10px;">
                <button class="btn btn-sm btn-secondary" onclick="window.approvalController.openEditModal('${job.job_id}', \`${this.escapeHtml(job.content)}\`)">
                  <i class="ri-edit-line"></i> Edit
                </button>
                <button class="btn btn-sm btn-danger" onclick="window.approvalController.handleReject('${job.job_id}')">
                  <i class="ri-close-circle-line"></i> Reject
                </button>
                <button class="btn btn-sm btn-success" onclick="window.approvalController.handleApprove('${job.job_id}')">
                  <i class="ri-check-line"></i> Approve & Publish
                </button>
              </div>
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
          <h4>Error Loading Approvals</h4>
          <p>${error.message}</p>
        </div>
      `;
    }
  }

  async handleApprove(jobId) {
    try {
      window.app.showToast("Approving and publishing post...", "info");
      const res = await window.api.reviewJob(jobId, "approve");
      
      if (res.success) {
        window.app.showToast("Post approved and published successfully!", "success");
      } else {
        window.app.showToast(`Post approved, but publishing returned: ${res.message}`, "warning");
      }

      await this.refreshData();
      if (window.dashboardController) window.dashboardController.refreshData();
      if (window.publishingController) window.publishingController.refreshData();
    } catch (error) {
      window.app.showToast(`Approval failed: ${error.message}`, "error");
    }
  }

  async handleReject(jobId) {
    try {
      await window.api.reviewJob(jobId, "reject");
      window.app.showToast("Post rejected.", "info");
      await this.refreshData();
      if (window.dashboardController) window.dashboardController.refreshData();
    } catch (error) {
      window.app.showToast(`Rejection failed: ${error.message}`, "error");
    }
  }

  openEditModal(jobId, currentContent) {
    document.getElementById("edit-job-id").value = jobId;
    document.getElementById("edit-job-content").value = currentContent;
    window.app.openModal("modal-edit-post");
  }

  async submitEdit() {
    const jobId = document.getElementById("edit-job-id").value;
    const content = document.getElementById("edit-job-content").value.trim();

    if (!content) {
      window.app.showToast("Content cannot be blank.", "error");
      return;
    }

    try {
      window.app.showToast("Saving edits and publishing...", "info");
      const res = await window.api.reviewJob(jobId, "edit", content);
      window.app.closeModal("modal-edit-post");

      if (res.success) {
        window.app.showToast("Post edited and published successfully!", "success");
      } else {
        window.app.showToast(`Post edited, but publishing status: ${res.message}`, "warning");
      }

      await this.refreshData();
      if (window.dashboardController) window.dashboardController.refreshData();
      if (window.publishingController) window.publishingController.refreshData();
    } catch (error) {
      window.app.showToast(`Edit failed: ${error.message}`, "error");
    }
  }

  escapeHtml(str) {
    if (!str) return "";
    return str.replace(/'/g, "&#39;").replace(/"/g, "&quot;");
  }
}

window.approvalController = new ApprovalCenterController();
