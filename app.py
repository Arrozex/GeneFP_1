from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__)

HF_API_URL = "https://yitxx-genefp.hf.space/run/predict"
HF_TOKEN = os.environ.get("HF_TOKEN")  # 你的 Hugging Face token（安全放這裡）

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "data": [user_input]
    }

    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        bot_reply = data["data"][0] if data.get("data") else "（模型無回應）"
    except Exception as e:
        print(f"錯誤：{e}")
        return jsonify({"reply": "❌ 抱歉，後端錯誤或模型沒回應"}), 500

    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)
