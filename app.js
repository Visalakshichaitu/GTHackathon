const chatWindow = document.getElementById("chat");
const input = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const locationInput = document.getElementById("location");

const API_URL = "http://127.0.0.1:8000/chat";
// For demo we use a fixed customer ID
const CUSTOMER_ID = "CUST-001";

function addMessage(text, sender) {
  const div = document.createElement("div");
  div.classList.add("message", sender);
  div.innerText = text;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendMessage() {
  const text = input.value.trim();
  if (!text) return;

  const location = locationInput.value.trim() || "Unknown";

  addMessage(text, "user");
  input.value = "";

  addMessage("Thinking...", "bot");
  const thinkingBubble = chatWindow.lastChild;

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        customer_id: CUSTOMER_ID,
        location: location,
      }),
    });

    const data = await res.json();
    thinkingBubble.innerText = data.reply;
  } catch (err) {
    thinkingBubble.innerText = "Sorry, something went wrong.";
    console.error(err);
  }
}

sendBtn.addEventListener("click", sendMessage);
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});
