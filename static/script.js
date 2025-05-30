async function sendMessage() {
  const input = document.getElementById("message");
  const chat = document.getElementById("chat");
  const userMessage = input.value.trim();
  
  if (!userMessage) return;
  
  // 顯示用戶訊息
  chat.innerHTML += `<p class="user"><b>你：</b> ${userMessage}</p>`;
  input.value = "";
  
  // 顯示載入狀態
  chat.innerHTML += `<p class="bot"><b>機器人：</b> 正在思考中...</p>`;
  
  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userMessage })
    });
    
    const data = await res.json();
    const reply = data.reply || "（沒有回應）";
    
    // 移除載入訊息並顯示回應
    const loadingMessage = chat.lastElementChild;
    loadingMessage.innerHTML = `<b>機器人：</b> ${reply}`;
    
  } catch (error) {
    console.error('錯誤:', error);
    const loadingMessage = chat.lastElementChild;
    loadingMessage.innerHTML = `<b>機器人：</b> ❌ 連線錯誤，請稍後再試`;
  }
  
  chat.scrollTop = chat.scrollHeight;
}

// 按 Enter 鍵也能送出訊息
document.getElementById("message").addEventListener("keypress", function(event) {
  if (event.key === "Enter") {
    sendMessage();
  }
});
