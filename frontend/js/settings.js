/**
 * settings.js — System Settings & Configuration Controller
 */

class SettingsController {
  async init() {
    await this.refreshData();
  }

  async refreshData() {
    try {
      const health = await window.api.getHealth();
      
      const apiStatusEl = document.getElementById("settings-api-status");
      const modelEl = document.getElementById("settings-model-name");
      const agentEl = document.getElementById("settings-agent-name");

      if (apiStatusEl) {
        if (health.status === "healthy") {
          apiStatusEl.innerHTML = `<span class="badge badge-published"><i class="ri-checkbox-circle-fill"></i> Healthy & Online</span>`;
        } else {
          apiStatusEl.innerHTML = `<span class="badge badge-failed"><i class="ri-close-circle-fill"></i> ${health.status}</span>`;
        }
      }

      if (modelEl) modelEl.textContent = health.model || "groq/llama-3.3-70b-versatile";
      if (agentEl) agentEl.textContent = health.agent || "social_media_master_agent";

    } catch (error) {
      console.error("Settings refresh error:", error);
    }
  }
}

window.settingsController = new SettingsController();
