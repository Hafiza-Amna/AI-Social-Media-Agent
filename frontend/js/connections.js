/**
 * connections.js — Social Media Account Connections Controller
 */

class SocialConnectionsController {
  async init() {
    await this.refreshData();
  }

  async refreshData() {
    try {
      const health = await window.api.getHealth();
      
      // Update LinkedIn connection card status
      const liStatusEl = document.getElementById("conn-linkedin-status");
      if (liStatusEl) {
        liStatusEl.innerHTML = `<span class="badge badge-published"><i class="ri-checkbox-circle-fill"></i> OAuth 2.0 Integration Ready</span>`;
      }

      // Update Instagram connection card status
      const igStatusEl = document.getElementById("conn-instagram-status");
      if (igStatusEl) {
        igStatusEl.innerHTML = `<span class="badge badge-published"><i class="ri-checkbox-circle-fill"></i> Graph API Integration Ready</span>`;
      }
    } catch (error) {
      console.error("Connections status error:", error);
    }
  }

  connectLinkedIn() {
    window.location.href = window.api.getLinkedInLoginUrl();
  }
}

window.connectionsController = new SocialConnectionsController();
