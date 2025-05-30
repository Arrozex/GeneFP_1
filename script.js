const chat = document.getElementById("chat");

async function sendMessage() {
  const input = document.getElementById("message");
  const userMessage = input.value.trim();
  if (!userMessage) return;

  chat.innerHTML += `<p class="user"><b>你：</b> ${userMessage}</p>`;
  input.value = "";

  const res = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: userMessage })
  });

  const data = await res.json();
  const reply = data.reply || "（沒有回應）";
  chat.innerHTML += `<p class="bot"><b>機器人：</b> ${reply}</p>`;
  chat.scrollTop = chat.scrollHeight;
}
