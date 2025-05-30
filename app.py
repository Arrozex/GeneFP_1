from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__)

HF_API_URL = "https://yitxx-genefp.hf.space/api/predict"
HF_TOKEN = os.environ.get("HF_TOKEN")  # 你的 Hugging Face token（安全放這裡）

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_input = request.json.get("message", "")
        if not user_input:
            return jsonify({"reply": "請輸入訊息"}), 400
        
        # 检查 HF_TOKEN 是否存在
        if not HF_TOKEN:
            return jsonify({"reply": "❌ 系統配置錯誤"}), 500
        
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # 根据你的API格式调整payload
        payload = {
            "inputs": user_input,  # 大多数HF模型使用 "inputs" 而不是 "data"
            "parameters": {
                "max_length": 200,
                "temperature": 0.7
            }
        }
        
        print(f"發送請求到: {HF_API_URL}")
        print(f"請求內容: {payload}")
        
        response = requests.post(
            HF_API_URL, 
            headers=headers, 
            json=payload,
            timeout=30  # 添加超时设置
        )
        
        print(f"回應狀態碼: {response.status_code}")
        print(f"回應內容: {response.text}")
        
        response.raise_for_status()
        data = response.json()
        
        # 根据API响应格式解析回复
        if isinstance(data, list) and len(data) > 0:
            bot_reply = data[0].get("generated_text", "(模型無回應)")
        elif isinstance(data, dict):
            bot_reply = data.get("generated_text", data.get("data", "(模型無回應)"))
        else:
            bot_reply = "(模型回應格式異常)"
            
    except requests.exceptions.Timeout:
        print("請求超時")
        return jsonify({"reply": "❌ 請求超時，請稍後再試"}), 500
    except requests.exceptions.RequestException as e:
        print(f"請求錯誤: {e}")
        return jsonify({"reply": "❌ 網路連接錯誤"}), 500
    except Exception as e:
        print(f"其他錯誤: {e}")
        return jsonify({"reply": "❌ 系統錯誤，請稍後再試"}), 500
    
    return jsonify({"reply": bot_reply})

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "頁面不存在"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "伺服器內部錯誤"}), 500

if __name__ == "__main__":
    # 生產環境配置
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
