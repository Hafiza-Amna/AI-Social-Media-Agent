/**
 * analytics.js — Analytics & Performance Insights Controller
 */

class AnalyticsController {
  async init() {
    await this.refreshData();
  }

  async refreshData() {
    try {
      const data = await window.api.getJobs();
      const jobs = data.jobs || [];

      const total = jobs.length;
      const published = jobs.filter(j => j.status === "published" || j.status === "Published").length;
      const pending = jobs.filter(j => j.status === "pending_review").length;
      const failed = jobs.filter(j => j.status === "failed" || j.status === "Failed").length;

      const linkedinCount = jobs.filter(j => (j.platform || "").toLowerCase() === "linkedin").length;
      const instagramCount = jobs.filter(j => (j.platform || "").toLowerCase() === "instagram").length;

      document.getElementById("analytics-total-posts").textContent = total;
      document.getElementById("analytics-published-posts").textContent = published;
      document.getElementById("analytics-pending-posts").textContent = pending;
      document.getElementById("analytics-failed-posts").textContent = failed;

      document.getElementById("analytics-linkedin-count").textContent = `${linkedinCount} posts`;
      document.getElementById("analytics-instagram-count").textContent = `${instagramCount} posts`;

    } catch (error) {
      console.error("Analytics refresh error:", error);
    }
  }
}

window.analyticsController = new AnalyticsController();
