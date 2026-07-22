/**
 * api.js — Centralized API Client for AI Social Media Agent FastAPI Backend
 */

const API_BASE_URL = window.location.origin;

class ApiClient {
  /**
   * Health check endpoint GET /health
   */
  async getHealth() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error("API Health Check Failed:", error);
      return { status: "offline", detail: error.message };
    }
  }

  /**
   * List jobs from database GET /jobs?status=...
   */
  async getJobs(status = null) {
    try {
      let url = `${API_BASE_URL}/jobs`;
      if (status) {
        url += `?status=${encodeURIComponent(status)}`;
      }
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error("Fetch Jobs Failed:", error);
      throw error;
    }
  }

  /**
   * Send prompt to Master Agent POST /chat
   */
  async sendChat(message, userId = "dashboard-user") {
    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, user_id: userId })
      });

      if (response.status === 429) {
        throw new Error("Rate limit exceeded (20 req/min). Please wait a moment before trying again.");
      }

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Send Chat Failed:", error);
      throw error;
    }
  }

  /**
   * Review pending job POST /review/{job_id}
   * Supported actions: 'approve', 'reject', 'edit'
   */
  async reviewJob(jobId, action, content = null, reviewer = "Human Reviewer") {
    try {
      const payload = { action, reviewer };
      if (action === "edit" && content) {
        payload.content = content;
      }

      const response = await fetch(`${API_BASE_URL}/review/${encodeURIComponent(jobId)}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`Review Job ${jobId} Failed:`, error);
      throw error;
    }
  }

  /**
   * Manually execute approved job POST /execute_job/{job_id}
   */
  async executeJob(jobId) {
    try {
      const response = await fetch(`${API_BASE_URL}/execute_job/${encodeURIComponent(jobId)}`, {
        method: "POST"
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`Execute Job ${jobId} Failed:`, error);
      throw error;
    }
  }

  /**
   * LinkedIn login redirect URL
   */
  getLinkedInLoginUrl() {
    return `${API_BASE_URL}/linkedin/login`;
  }
}

window.api = new ApiClient();
