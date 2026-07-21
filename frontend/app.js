// ---- Config ----
// Adjust this if your backend exposes health checks at a different path.
const HEALTH_ENDPOINT = "/health";
const HEALTH_POLL_MS = 30000;

// ---- Elements ----
const chat = document.getElementById("chat");
const input = document.getElementById("input");
const thinking = document.getElementById("thinking");
const apiKeyInput = document.getElementById("api-key-input");
const apiKeySubmit = document.getElementById("api-key-submit");
const apiKeyStatus = document.getElementById("api-key-status");
const settingsToggle = document.getElementById("settings-toggle");
const settingsPanel = document.getElementById("settings-panel");
const aboutToggle = document.getElementById("about-toggle");
const chatToggle = document.getElementById("chat-toggle");
const aboutView = document.getElementById("about-view");
const chatView = document.getElementById("chat-view");
const sampleDataTable = document.getElementById("sample-data-table");
const statusDot = document.getElementById("status-dot");
const statusText = document.getElementById("status-text");
const exampleModal = document.getElementById("example-modal");
const openExamplesButtons = [
  document.getElementById("open-examples"),
  document.getElementById("open-examples-footer"),
].filter(Boolean);
const closeExamplesButton = document.getElementById("close-examples");

// Session state
let sessionId = null;
let sessionConfigured = false;

// ---- View switching (Chat <-> About) ----
function showChatView() {
  chatView.classList.remove("hidden");
  aboutView.classList.add("hidden");
  chatToggle.classList.add("text-blue-600");
  chatToggle.classList.remove("text-gray-600", "hover:text-blue-600");
  aboutToggle.classList.remove("text-blue-600");
  aboutToggle.classList.add("text-gray-600", "hover:text-blue-600");
}

function showAboutView() {
  aboutView.classList.remove("hidden");
  chatView.classList.add("hidden");
  aboutToggle.classList.add("text-blue-600");
  aboutToggle.classList.remove("text-gray-600", "hover:text-blue-600");
  chatToggle.classList.remove("text-blue-600");
  chatToggle.classList.add("text-gray-600", "hover:text-blue-600");
}

chatToggle.addEventListener("click", showChatView);
aboutToggle.addEventListener("click", showAboutView);

// ---- Example questions modal ----
function openExampleModal() {
  exampleModal.classList.remove("hidden");
}

function closeExampleModal() {
  exampleModal.classList.add("hidden");
}

openExamplesButtons.forEach((btn) => btn.addEventListener("click", openExampleModal));
closeExamplesButton.addEventListener("click", closeExampleModal);

// Click outside the card closes it
exampleModal.addEventListener("click", (e) => {
  if (e.target === exampleModal) closeExampleModal();
});

// Escape key closes it
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !exampleModal.classList.contains("hidden")) {
    closeExampleModal();
  }
});

// ---- Sample data (About page) ----
const SAMPLE_FLIGHTS = [
  { flight: 2199, departure: "19:00", length: "01:59", airline: "DL", from: "MEM", to: "MCO", day: "Thu", delayed: "yes" },
  { flight: 32, departure: "13:47", length: "03:43", airline: "UA", from: "DEN", to: "EWR", day: "Thu", delayed: "yes" },
  { flight: 1050, departure: "15:35", length: "01:00", airline: "WN", from: "BWI", to: "PIT", day: "Mon", delayed: "yes" },
  { flight: 379, departure: "13:34", length: "02:21", airline: "DL", from: "BUF", to: "ATL", day: "Tue", delayed: "no" },
  { flight: 238, departure: "22:19", length: "04:37", airline: "UA", from: "SAN", to: "IAD", day: "Sun", delayed: "no" },
];

function renderSampleData() {
  sampleDataTable.innerHTML = "";
  SAMPLE_FLIGHTS.forEach((row, i) => {
    const tr = document.createElement("tr");
    tr.className = i % 2 === 0 ? "bg-white" : "bg-gray-50";
    tr.className += " border-b border-gray-100 last:border-0";

    const delayBadge =
      row.delayed === "yes"
        ? '<span class="inline-block px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700">yes</span>'
        : '<span class="inline-block px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-700">no</span>';

    tr.innerHTML = `
      <td class="px-4 py-2 text-gray-700">${row.flight}</td>
      <td class="px-4 py-2 text-gray-700">${row.departure}</td>
      <td class="px-4 py-2 text-gray-700">${row.length}</td>
      <td class="px-4 py-2 text-gray-700">${row.airline}</td>
      <td class="px-4 py-2 text-gray-700">${row.from}</td>
      <td class="px-4 py-2 text-gray-700">${row.to}</td>
      <td class="px-4 py-2 text-gray-700">${row.day}</td>
      <td class="px-4 py-2">${delayBadge}</td>
    `;
    sampleDataTable.appendChild(tr);
  });
}

// ---- Backend health check ----
async function checkBackendHealth() {
  try {
    const res = await fetch(HEALTH_ENDPOINT, { method: "GET" });
    if (res.ok) {
      statusDot.className = "w-2 h-2 rounded-full bg-emerald-500";
      statusText.textContent = "Backend online";
      statusText.className = "text-emerald-600";
    } else {
      throw new Error("Non-200 response");
    }
  } catch (err) {
    statusDot.className = "w-2 h-2 rounded-full bg-red-500";
    statusText.textContent = "Backend offline";
    statusText.className = "text-red-600";
  }
}

// ---- Settings panel ----
settingsToggle.addEventListener("click", () => {
  settingsPanel.classList.toggle("hidden");
});

// Submit API key: create session then configure it
apiKeySubmit.addEventListener("click", async () => {
  const key = apiKeyInput.value.trim();
  if (!key) {
    apiKeyStatus.innerText = "Please enter a valid API key.";
    apiKeyStatus.className = "text-sm mt-2 font-semibold text-red-600";
    return;
  }

  apiKeyStatus.innerText = "Setting up session…";
  apiKeyStatus.className = "text-sm mt-2 font-semibold text-gray-500";

  try {
    // 1. Create session
    const createRes = await fetch("/session/create", { method: "POST" });
    if (!createRes.ok) throw new Error("Failed to create session.");
    const createData = await createRes.json();
    sessionId = createData.session_id;

    // 2. Configure session with API key
    const configRes = await fetch("/session/configure", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, api_key: key }),
    });
    if (!configRes.ok) throw new Error("Failed to configure session.");

    sessionConfigured = true;
    apiKeyStatus.innerText = "✓ API key submitted. Session started.";
    apiKeyStatus.className = "text-sm mt-2 font-semibold text-emerald-600";
  } catch (err) {
    sessionId = null;
    sessionConfigured = false;
    apiKeyStatus.innerText = "Error: " + err.message;
    apiKeyStatus.className = "text-sm mt-2 font-semibold text-red-600";
  }
});

// Delete session when the page/tab closes
window.addEventListener("beforeunload", () => {
  if (sessionId) {
    navigator.sendBeacon(
      "/session/delete",
      new Blob([JSON.stringify({ session_id: sessionId })], {
        type: "application/json",
      })
    );
  }
});

// ---- Chat messages ----

// Fields we never want surfaced in the message dialog (e.g. stray
// disclaimers like "no api key required" that some backends echo back
// inside metrics/meta payloads).
const HIDDEN_META_PATTERN = /api[\s_-]?key/i;

function sanitizeMeta(meta) {
  if (!meta || typeof meta !== "object") return meta;
  const clean = {};
  for (const [key, value] of Object.entries(meta)) {
    const text = `${key} ${value}`;
    if (HIDDEN_META_PATTERN.test(text)) continue;
    clean[key] = value;
  }
  return Object.keys(clean).length ? clean : null;
}

const welcome = document.getElementById("welcome");

function addMessage(role, text, meta = null) {
  if (welcome && !welcome.classList.contains("hidden")) {
    welcome.classList.add("hidden");
  }

  const wrapper = document.createElement("div");
  wrapper.className = role === "user" ? "text-right mb-4" : "text-left mb-4";

  const bubble = document.createElement("div");
  bubble.className =
    "inline-block px-4 py-2 rounded-2xl max-w-xl whitespace-pre-wrap text-sm " +
    (role === "user"
      ? "bg-blue-600 text-white"
      : "bg-white shadow-sm border border-gray-200");

  bubble.innerText = text;
  wrapper.appendChild(bubble);

  const cleanMeta = sanitizeMeta(meta);
  if (cleanMeta) {
    const metaDiv = document.createElement("div");
    metaDiv.className = "text-xs text-gray-400 mt-1";
    metaDiv.innerText = JSON.stringify(cleanMeta);
    wrapper.appendChild(metaDiv);
  }

  chat.appendChild(wrapper);
  chat.scrollTop = chat.scrollHeight;
}

async function sendMessage() {
  const query = input.value.trim();
  if (!query) return;

  if (!sessionConfigured) {
    addMessage("assistant", "Please submit your API key in Settings before asking questions.");
    return;
  }

  addMessage("user", query);
  input.value = "";

  thinking.classList.remove("hidden");

  try {
    const res = await fetch("/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: query,
        session_id: sessionId,
      }),
    });

    const data = await res.json();

    if (!res.ok) {
      addMessage("assistant", "Error: " + (data.detail || res.statusText));
    } else {
      addMessage("assistant", data.answer || "No answer returned", data.metrics);
    }
  } catch (err) {
    addMessage("assistant", "Error: " + err.message);
  } finally {
    thinking.classList.add("hidden");
  }
}

// Enter key support
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});

// Example question buttons (inside the modal)
document.querySelectorAll(".example-question").forEach((btn) => {
  btn.addEventListener("click", () => {
    input.value = btn.textContent.trim();
    closeExampleModal();
    sendMessage();
  });
});

// ---- Init ----
renderSampleData();
checkBackendHealth();
setInterval(checkBackendHealth, HEALTH_POLL_MS);