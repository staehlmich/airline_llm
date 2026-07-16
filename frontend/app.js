const chat = document.getElementById("chat");
const input = document.getElementById("input");
const thinking = document.getElementById("thinking");
const apiKeyInput = document.getElementById("api-key-input");
const apiKeySubmit = document.getElementById("api-key-submit");
const apiKeyStatus = document.getElementById("api-key-status");
const settingsToggle = document.getElementById("settings-toggle");
const settingsPanel = document.getElementById("settings-panel");

// Session state
let sessionId = null;
let sessionConfigured = false;

// Toggle settings panel
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

function addMessage(role, text, meta = null) {
  const wrapper = document.createElement("div");
  wrapper.className = role === "user" ? "text-right" : "text-left";

  const bubble = document.createElement("div");
  bubble.className =
    "inline-block px-3 py-2 rounded-lg max-w-xl whitespace-pre-wrap " +
    (role === "user" ? "bg-blue-600 text-white" : "bg-white shadow");

  bubble.innerText = text;
  wrapper.appendChild(bubble);

  if (meta) {
    const metaDiv = document.createElement("div");
    metaDiv.className = "text-xs text-gray-400 mt-1";
    metaDiv.innerText = JSON.stringify(meta);
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
