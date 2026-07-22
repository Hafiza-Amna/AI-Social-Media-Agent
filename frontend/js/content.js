/**
 * content.js — AI Content Generator Section Controller
 */

class ContentGeneratorController {
  init() {
    const form = document.getElementById("content-gen-form");
    if (form) {
      form.addEventListener("submit", (e) => this.handleGenerate(e));
    }
  }

  async handleGenerate(e) {
    e.preventDefault();
    const platform = document.getElementById("gen-platform").value;
    const topic = document.getElementById("gen-topic").value.trim();
    const tone = document.getElementById("gen-tone").value;
    const contentType = document.getElementById("gen-type").value;
    const mediaUrl = document.getElementById("gen-media-url") ? document.getElementById("gen-media-url").value.trim() : "";

    if (!topic) {
      window.app.showToast("Please enter a topic or content prompt.", "error");
      return;
    }

    const btn = document.getElementById("btn-generate-content");
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span> Generating AI Content...`;

    try {
      let promptMessage = "";
      if (contentType === "ab_variant") {
        promptMessage = `Generate A/B caption variants for a ${platform} post about: ${topic}. Tone: ${tone}.`;
      } else if (platform === "Instagram") {
        const urlToUse = mediaUrl || "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800";
        promptMessage = `Generate and publish an Instagram post about: ${topic}. Tone: ${tone}. Use image URL: ${urlToUse}`;
      } else {
        promptMessage = `Generate and publish a LinkedIn post about: ${topic}. Tone: ${tone}.`;
      }

      const res = await window.api.sendChat(promptMessage);
      
      this.displayResult(res, platform, topic);
      window.app.showToast("Content generated successfully!", "success");
      
      // Refresh approval center and dashboard
      if (window.approvalController) window.approvalController.refreshData();
      if (window.dashboardController) window.dashboardController.refreshData();

    } catch (error) {
      window.app.showToast(error.message || "Failed to generate content.", "error");
    } finally {
      btn.disabled = false;
      btn.innerHTML = originalText;
    }
  }

  displayResult(res, platform, topic) {
    const outputCard = document.getElementById("gen-output-card");
    const outputText = document.getElementById("gen-output-text");
    const outputMeta = document.getElementById("gen-output-meta");

    if (!outputCard || !outputText) return;

    outputCard.style.display = "block";
    outputText.value = res.response || "No response content generated.";

    let metaHtml = `<span class="platform-badge ${platform.toLowerCase()}"><i class="ri-${platform.toLowerCase()}-fill"></i> ${platform}</span>`;
    if (res.job_id) {
      metaHtml += ` | <span class="badge badge-pending">Queued Job ID: ${res.job_id}</span>`;
    }
    outputMeta.innerHTML = metaHtml;
  }

  copyContent() {
    const outputText = document.getElementById("gen-output-text");
    if (outputText && outputText.value) {
      navigator.clipboard.writeText(outputText.value);
      window.app.showToast("Content copied to clipboard!", "info");
    }
  }
}

window.contentController = new ContentGeneratorController();
