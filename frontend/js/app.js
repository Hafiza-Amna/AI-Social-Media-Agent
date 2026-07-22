/**
 * app.js — Main Application SPA Router, State & Modal Manager
 */

class Application {
  constructor() {
    this.currentTab = "dashboard";
  }

  init() {
    this.setupNavigation();
    this.setupMobileToggle();
    this.checkHealth();
    this.switchTab("dashboard");
  }

  setupNavigation() {
    document.querySelectorAll(".nav-item").forEach(item => {
      item.addEventListener("click", (e) => {
        e.preventDefault();
        const tab = item.dataset.tab;
        if (tab) this.switchTab(tab);
      });
    });
  }

  setupMobileToggle() {
    const toggle = document.getElementById("mobile-menu-toggle");
    const sidebar = document.querySelector(".sidebar");
    if (toggle && sidebar) {
      toggle.addEventListener("click", () => {
        sidebar.classList.toggle("open");
      });
    }
  }

  async checkHealth() {
    const health = await window.api.getHealth();
    const statusDot = document.getElementById("header-status-indicator");
    const statusText = document.getElementById("header-status-text");

    if (statusDot && statusText) {
      if (health.status === "healthy") {
        statusDot.className = "status-indicator online";
        statusText.textContent = "API Operational";
      } else {
        statusDot.className = "status-indicator offline";
        statusText.textContent = "API Disconnected";
      }
    }
  }

  switchTab(tabId) {
    this.currentTab = tabId;

    // Update sidebar nav active state
    document.querySelectorAll(".nav-item").forEach(item => {
      if (item.dataset.tab === tabId) {
        item.classList.add("active");
      } else {
        item.classList.remove("active");
      }
    });

    // Update section active state
    document.querySelectorAll(".view-section").forEach(sec => {
      sec.classList.remove("active");
    });

    const activeSec = document.getElementById(`section-${tabId}`);
    if (activeSec) {
      activeSec.classList.add("active");
    }

    // Update Header title
    const titleEl = document.getElementById("page-title-text");
    if (titleEl) {
      const titlesMap = {
        dashboard: "Dashboard Overview",
        content: "AI Content Generator",
        approval: "Content Approval Center",
        calendar: "Content Calendar",
        connections: "Social Media Connections",
        publishing: "Publishing Queue Center",
        analytics: "Analytics & Performance",
        settings: "System Settings & Configuration"
      };
      titleEl.textContent = titlesMap[tabId] || "Dashboard";
    }

    // Trigger controller refresh
    if (tabId === "dashboard" && window.dashboardController) window.dashboardController.init();
    if (tabId === "content" && window.contentController) window.contentController.init();
    if (tabId === "approval" && window.approvalController) window.approvalController.init();
    if (tabId === "calendar" && window.calendarController) window.calendarController.init();
    if (tabId === "connections" && window.connectionsController) window.connectionsController.init();
    if (tabId === "publishing" && window.publishingController) window.publishingController.init();
    if (tabId === "analytics" && window.analyticsController) window.analyticsController.init();
    if (tabId === "settings" && window.settingsController) window.settingsController.init();

    // Close mobile sidebar if open
    const sidebar = document.querySelector(".sidebar");
    if (sidebar) sidebar.classList.remove("open");
  }

  showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    
    let iconClass = "ri-information-line";
    if (type === "success") iconClass = "ri-checkbox-circle-line";
    if (type === "error") iconClass = "ri-error-warning-line";
    if (type === "warning") iconClass = "ri-alert-line";

    toast.innerHTML = `
      <div style="display: flex; align-items: center; gap: 10px;">
        <i class="${iconClass}" style="font-size: 18px;"></i>
        <span>${message}</span>
      </div>
      <i class="ri-close-line" style="cursor: pointer;" onclick="this.parentElement.remove()"></i>
    `;

    container.appendChild(toast);
    setTimeout(() => {
      if (toast.parentElement) toast.remove();
    }, 4500);
  }

  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.add("active");
  }

  closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.remove("active");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  window.app = new Application();
  window.app.init();
});
