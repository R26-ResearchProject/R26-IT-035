function splitCsv(value) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter((item) => item.length > 0);
}

function isDevMode() {
  const params = new URLSearchParams(window.location.search);
  const devParam = params.get("dev");
  if (devParam === "1" || devParam === "true") return true;
  try {
    return window.localStorage.getItem("dev_tools") === "1";
  } catch (e) {
    return false;
  }
}

function applyDevModeVisibility() {
  const devTools = document.getElementById("dev-tools");
  if (!devTools) return;
  if (isDevMode()) {
    devTools.classList.remove("is-hidden");
    setStatus("Developer tools enabled (payload + mock integration).");
  }
}

const SCENARIOS = {
  vata_eczema: {
    user_id: "U101",
    prakriti_result: {
      dominant_prakriti: "Vata",
      secondary_prakriti: "Pitta",
      prakriti_scores: { vata: 0.72, pitta: 0.2, kapha: 0.08 },
      confidence: 0.81,
    },
    skin_result: {
      predicted_condition: "Eczema",
      confidence: 0.87,
      severity: "mild",
      symptoms: ["dryness", "itching", "redness"],
      referral_required: false,
    },
    user_context: {
      age_group: "adult",
      known_allergies: [],
      pregnancy_status: false,
      preferred_language: "English",
    },
  },
  pitta_acne: {
    user_id: "U102",
    prakriti_result: {
      dominant_prakriti: "Pitta",
      secondary_prakriti: "Vata",
      prakriti_scores: { vata: 0.2, pitta: 0.7, kapha: 0.1 },
      confidence: 0.83,
    },
    skin_result: {
      predicted_condition: "Acne",
      confidence: 0.86,
      severity: "moderate",
      symptoms: ["redness", "oiliness", "inflammation"],
      referral_required: false,
    },
    user_context: {
      age_group: "adult",
      known_allergies: [],
      pregnancy_status: false,
      preferred_language: "English",
    },
  },
  kapha_fungal: {
    user_id: "U103",
    prakriti_result: {
      dominant_prakriti: "Kapha",
      secondary_prakriti: "Pitta",
      prakriti_scores: { vata: 0.05, pitta: 0.25, kapha: 0.7 },
      confidence: 0.79,
    },
    skin_result: {
      predicted_condition: "Fungal Infection",
      confidence: 0.84,
      severity: "moderate",
      symptoms: ["itching", "moist_patches", "sweating"],
      referral_required: false,
    },
    user_context: {
      age_group: "adult",
      known_allergies: [],
      pregnancy_status: false,
      preferred_language: "English",
    },
  },
  low_confidence: {
    user_id: "U104",
    prakriti_result: {
      dominant_prakriti: "Vata",
      secondary_prakriti: "Pitta",
      prakriti_scores: { vata: 0.55, pitta: 0.3, kapha: 0.15 },
      confidence: 0.4,
    },
    skin_result: {
      predicted_condition: "Eczema",
      confidence: 0.55,
      severity: "mild",
      symptoms: ["dryness", "itching"],
      referral_required: false,
    },
    user_context: {
      age_group: "adult",
      known_allergies: [],
      pregnancy_status: false,
      preferred_language: "English",
    },
  },
  severe_case: {
    user_id: "U105",
    prakriti_result: {
      dominant_prakriti: "Pitta",
      secondary_prakriti: "Vata",
      prakriti_scores: { vata: 0.2, pitta: 0.65, kapha: 0.15 },
      confidence: 0.8,
    },
    skin_result: {
      predicted_condition: "Psoriasis",
      confidence: 0.88,
      severity: "severe",
      symptoms: ["thick_scaling", "redness", "dryness"],
      referral_required: false,
    },
    user_context: {
      age_group: "adult",
      known_allergies: [],
      pregnancy_status: false,
      preferred_language: "English",
    },
  },
};

let lastOutput = null;
let lastPayload = null;

function setStatus(message) {
  document.getElementById("status-box").textContent = message;
}

function formToPayload() {
  return {
    user_id: document.getElementById("user_id").value.trim(),
    prakriti_result: {
      dominant_prakriti: document.getElementById("dominant_prakriti").value,
      secondary_prakriti: document.getElementById("secondary_prakriti").value,
      prakriti_scores: {
        vata: Number(document.getElementById("score_vata").value),
        pitta: Number(document.getElementById("score_pitta").value),
        kapha: Number(document.getElementById("score_kapha").value),
      },
      confidence: Number(document.getElementById("prakriti_confidence").value),
    },
    skin_result: {
      predicted_condition: document.getElementById("predicted_condition").value,
      confidence: Number(document.getElementById("skin_confidence").value),
      severity: document.getElementById("severity").value,
      symptoms: splitCsv(document.getElementById("symptoms").value),
      referral_required: document.getElementById("referral_required").checked,
    },
    user_context: {
      age_group: document.getElementById("age_group").value,
      known_allergies: splitCsv(document.getElementById("known_allergies").value),
      pregnancy_status: document.getElementById("pregnancy_status").checked,
      preferred_language: document.getElementById("preferred_language").value.trim() || "English",
      dietary_preference: document.getElementById("dietary_preference").value,
    },
  };
}

function applyPayloadToForm(payload) {
  document.getElementById("user_id").value = payload.user_id || "";
  document.getElementById("dominant_prakriti").value = payload.prakriti_result.dominant_prakriti;
  document.getElementById("secondary_prakriti").value = payload.prakriti_result.secondary_prakriti;
  document.getElementById("score_vata").value = payload.prakriti_result.prakriti_scores.vata;
  document.getElementById("score_pitta").value = payload.prakriti_result.prakriti_scores.pitta;
  document.getElementById("score_kapha").value = payload.prakriti_result.prakriti_scores.kapha;
  document.getElementById("prakriti_confidence").value = payload.prakriti_result.confidence;

  document.getElementById("predicted_condition").value = payload.skin_result.predicted_condition;
  document.getElementById("skin_confidence").value = payload.skin_result.confidence;
  document.getElementById("severity").value = payload.skin_result.severity;
  document.getElementById("symptoms").value = (payload.skin_result.symptoms || []).join(", ");
  document.getElementById("referral_required").checked = !!payload.skin_result.referral_required;

  document.getElementById("age_group").value = payload.user_context.age_group;
  document.getElementById("known_allergies").value = (payload.user_context.known_allergies || []).join(", ");
  document.getElementById("pregnancy_status").checked = !!payload.user_context.pregnancy_status;
  document.getElementById("preferred_language").value = payload.user_context.preferred_language || "English";
  document.getElementById("dietary_preference").value = payload.user_context.dietary_preference || "";
}

const CATEGORY_LABELS = { diet: "Diet", lifestyle: "Lifestyle", home_care: "Home Care" };
let activeCategory = "diet";

function renderOutput(result) {
  const summaryBox = document.getElementById("summary-box");
  const outputBox = document.getElementById("recommendation-output");
  summaryBox.innerHTML = "";
  outputBox.innerHTML = "";

  lastOutput = result;
  const confidence = result.overall_confidence_level || "low";
  summaryBox.innerHTML = `
    <div class="summary-box">
      <strong>${result.recommendation_summary || "No summary provided."}</strong>
      <span class="badge ${confidence}">${confidence}</span>
      <p>${result.explanation_summary || ""}</p>
      <p class="meta">${result.safety_note || ""}</p>
    </div>
  `;

  if (result.referral_warning) {
    const warning = document.createElement("div");
    warning.className = "warning";
    warning.textContent = result.referral_warning;
    outputBox.appendChild(warning);
  }

  const grouped = result.recommendations_by_category || {};
  const categories = ["diet", "lifestyle", "home_care"];

  // Default to the first category that actually has items.
  if (!grouped[activeCategory] || grouped[activeCategory].length === 0) {
    activeCategory = categories.find((cat) => (grouped[cat] || []).length > 0) || "diet";
  }

  const tabBar = document.createElement("div");
  tabBar.className = "category-tabs";
  categories.forEach((category) => {
    const items = grouped[category] || [];
    const tab = document.createElement("button");
    tab.type = "button";
    tab.className = "category-tab" + (category === activeCategory ? " active" : "");
    tab.textContent = `${CATEGORY_LABELS[category]} (${items.length})`;
    tab.addEventListener("click", () => {
      activeCategory = category;
      renderOutput(result);
    });
    tabBar.appendChild(tab);
  });
  outputBox.appendChild(tabBar);

  const panel = document.createElement("div");
  panel.className = "category-panel";
  const items = grouped[activeCategory] || [];

  if (items.length === 0) {
    const empty = document.createElement("p");
    empty.className = "meta";
    empty.textContent = "No recommendations in this category.";
    panel.appendChild(empty);
  }

  items.forEach((item) => {
    const card = document.createElement("div");
    card.className = "rec-card";
    card.innerHTML = `
      <div class="rec-card-head">
        <strong>${item.title}</strong>
        <span class="score-pill">${Math.round(item.score * 100)}%</span>
      </div>
      <p>${item.text}</p>
      <p class="meta">Matched: ${item.matched_factors.prakriti}, ${item.matched_factors.condition}</p>
      <details class="rec-details">
        <summary>Why this was recommended</summary>
        <p class="meta"><em>${item.reason}</em></p>
        <p class="meta">${item.confidence_explanation}</p>
      </details>
    `;
    panel.appendChild(card);
  });

  outputBox.appendChild(panel);
}

function validatePayload(payload) {
  if (!payload.user_id) {
    throw new Error("user_id is required.");
  }
  if (!payload.skin_result.symptoms || payload.skin_result.symptoms.length === 0) {
    throw new Error("At least one symptom is required.");
  }
}

async function runRecommendation(event) {
  event.preventDefault();
  const payload = formToPayload();
  const topK = Number(document.getElementById("top_k").value || "6");
  setStatus("Running recommendation engine...");

  try {
    validatePayload(payload);
    const response = await fetch(`/api/recommend?top_k=${topK}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.message || "Failed to generate recommendations.");
    }
    renderOutput(result);
    lastPayload = payload;
    setFollowupEnabled(true);
    document.getElementById("download-pdf").disabled = false;
    clearFollowupLog();
    if (!chatOpen) {
      showChatBadge();
    }
    setStatus(`Done. Status: ${result.status}`);
  } catch (error) {
    setStatus(`Error: ${error.message}`);
  }
}

async function downloadPdfReport() {
  if (!lastPayload) {
    setStatus("Run the engine before downloading a PDF report.");
    return;
  }
  const topK = Number(document.getElementById("top_k").value || "6");
  setStatus("Generating PDF report...");

  try {
    const response = await fetch(`/api/report/pdf?top_k=${topK}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(lastPayload),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || "Failed to generate PDF report.");
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `recommendation_report_${lastPayload.user_id || "user"}.pdf`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    setStatus("PDF report downloaded.");
  } catch (error) {
    setStatus(`Error: ${error.message}`);
  }
}

let chatOpen = false;

function setFollowupEnabled(enabled) {
  document.getElementById("followup-question").disabled = !enabled;
  document.getElementById("followup-submit").disabled = !enabled;
  document.getElementById("chat-launcher").disabled = !enabled;
}

function clearFollowupLog() {
  document.getElementById("followup-log").innerHTML = "";
  updateChatEmptyState();
}

function updateChatEmptyState() {
  const log = document.getElementById("followup-log");
  const empty = document.getElementById("chat-empty-state");
  const suggestions = document.getElementById("chat-suggestions");
  const hasMessages = log.children.length > 0;
  empty.classList.toggle("is-hidden", hasMessages);
  suggestions.classList.toggle("is-hidden", hasMessages);
}

function showChatBadge() {
  document.getElementById("chat-launcher-badge").classList.remove("is-hidden");
}

function hideChatBadge() {
  document.getElementById("chat-launcher-badge").classList.add("is-hidden");
}

function openChat() {
  chatOpen = true;
  document.getElementById("chat-popup").classList.remove("is-hidden");
  hideChatBadge();
  document.getElementById("followup-question").focus();
}

function closeChat() {
  chatOpen = false;
  document.getElementById("chat-popup").classList.add("is-hidden");
}

function toggleChat() {
  if (chatOpen) {
    closeChat();
  } else {
    openChat();
  }
}

function appendFollowupEntry(question, answer, isLoading) {
  const log = document.getElementById("followup-log");
  const entry = document.createElement("div");
  entry.className = "followup-entry";
  const answerClass = isLoading ? "followup-answer is-loading" : "followup-answer";
  entry.innerHTML = `
    <p class="followup-question">${question}</p>
    <p class="${answerClass}">${answer}</p>
  `;
  log.appendChild(entry);
  log.scrollTop = log.scrollHeight;
  updateChatEmptyState();
  return entry.querySelector(".followup-answer");
}

async function askFollowupText(question) {
  if (!question || !lastPayload) return;
  const topK = Number(document.getElementById("top_k").value || "6");
  const answerEl = appendFollowupEntry(question, "Thinking...", true);

  try {
    const response = await fetch("/api/followup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, payload: lastPayload, top_k: topK }),
    });
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.message || "Follow-up question failed.");
    }
    answerEl.textContent = result.answer;
    answerEl.classList.remove("is-loading");
    if (result.source === "ai") {
      const tag = document.createElement("span");
      tag.className = "ai-tag";
      tag.textContent = "AI-assisted";
      answerEl.appendChild(document.createElement("br"));
      answerEl.appendChild(tag);
    }
  } catch (error) {
    answerEl.textContent = `Error: ${error.message}`;
    answerEl.classList.remove("is-loading");
  }
}

async function askFollowup(event) {
  event.preventDefault();
  const input = document.getElementById("followup-question");
  const question = input.value.trim();
  if (!question) return;
  input.value = "";
  await askFollowupText(question);
}

async function simulateModuleFetch(moduleName) {
  try {
    setStatus(`Simulating ${moduleName} module fetch...`);
    const response = await fetch(`/api/module-sim/${moduleName}`);
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.message || `Failed ${moduleName} simulation`);
    }

    const current = formToPayload();
    if (moduleName === "prakriti") {
      current.prakriti_result = result.data;
    } else if (moduleName === "skin") {
      current.skin_result = result.data;
    }
    applyPayloadToForm(current);
    setStatus(`${moduleName} module response applied to form.`);
  } catch (error) {
    setStatus(`Error: ${error.message}`);
  }
}

function exportFormJson() {
  const payload = formToPayload();
  document.getElementById("payload_json").value = JSON.stringify(payload, null, 2);
  setStatus("Form JSON exported to payload area.");
}

function applyJsonToForm() {
  try {
    const raw = document.getElementById("payload_json").value.trim();
    if (!raw) {
      throw new Error("Payload JSON area is empty.");
    }
    const parsed = JSON.parse(raw);
    applyPayloadToForm(parsed);
    setStatus("JSON payload applied to form.");
  } catch (error) {
    setStatus(`Error: ${error.message}`);
  }
}

function downloadOutputJson() {
  if (!lastOutput) {
    setStatus("No output available to download yet.");
    return;
  }
  const blob = new Blob([JSON.stringify(lastOutput, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "ui_output.json";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
  setStatus("Output JSON downloaded.");
}

function loadScenario(name) {
  const scenario = SCENARIOS[name];
  if (!scenario) {
    setStatus(`Unknown scenario: ${name}`);
    return;
  }
  applyPayloadToForm(scenario);
  setStatus(`Scenario loaded: ${name}`);
}

document.getElementById("recommendation-form").addEventListener("submit", runRecommendation);
document.getElementById("load-sample").addEventListener("click", async () => {
  const response = await fetch("/api/sample-input");
  const sample = await response.json();
  applyPayloadToForm(sample);
  setStatus("Sample input loaded.");
});
document.getElementById("reset-form").addEventListener("click", () => {
  document.getElementById("recommendation-form").reset();
  setStatus("Form reset.");
});
document.getElementById("mock-prakriti").addEventListener("click", () => simulateModuleFetch("prakriti"));
document.getElementById("mock-skin").addEventListener("click", () => simulateModuleFetch("skin"));
document.getElementById("export-json").addEventListener("click", exportFormJson);
document.getElementById("apply-json").addEventListener("click", applyJsonToForm);
document.getElementById("download-output").addEventListener("click", downloadOutputJson);
document.getElementById("download-pdf").addEventListener("click", downloadPdfReport);
document.querySelectorAll(".scenario-btn").forEach((button) => {
  button.addEventListener("click", () => loadScenario(button.dataset.scenario));
});
document.getElementById("followup-form").addEventListener("submit", askFollowup);
document.getElementById("chat-launcher").addEventListener("click", toggleChat);
document.getElementById("chat-popup-close").addEventListener("click", closeChat);
document.querySelectorAll(".chip-btn").forEach((chip) => {
  chip.addEventListener("click", () => askFollowupText(chip.dataset.question));
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && chatOpen) {
    closeChat();
  }
});
updateChatEmptyState();

applyPayloadToForm(window.__SAMPLE_INPUT__);
applyDevModeVisibility();
