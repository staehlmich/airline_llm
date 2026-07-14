const chat = document.getElementById("chat");
const input = document.getElementById("input");
const thinking = document.getElementById("thinking");
const apiKeyInput = document.getElementById("api-key-input");
const settingsToggle = document.getElementById("settings-toggle");
const settingsPanel = document.getElementById("settings-panel");

// Use relative URL so it works both locally and when served by FastAPI
const API_URL = "/query";

// Toggle settings panel
settingsToggle.addEventListener("click", () => {
  settingsPanel.classList.toggle("hidden");
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

  addMessage("user", query);
  input.value = "";

  thinking.classList.remove("hidden");

  try {
    const headers = { "Content-Type": "application/json" };

    // Attach BYOK key if provided
    const apiKey = apiKeyInput.value.trim();
    if (apiKey) {
      headers["X-OpenAI-Key"] = apiKey;
    }

    const res = await fetch(API_URL, {
      method: "POST",
      headers: headers,
      body: JSON.stringify({
        question: query,
        session_id: "default_session",
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
