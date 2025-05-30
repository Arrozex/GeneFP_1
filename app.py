from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__)

# 多個可能的API端點，按優先級排列
POSSIBLE_ENDPOINTS = [
    "https://yitxx-genefp.hf.space/api/predict",
    "https://yitxx-genefp.hf.space/call/predict", 
    "https://yitxx-genefp.hf.space/gradio_api/predict",
    "https://yitxx-genefp.hf.space/run/predict"
]

HF_TOKEN = os.environ.get("HF_TOKEN")  # 從環境變數獲取token

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_input = request.json.get("message", "")
        if not user_input:
            return jsonify({"reply": "請輸入訊息"}), 400
        
        # 檢查 HF_TOKEN 是否存在
        if not HF_TOKEN:
            return jsonify({"reply": "❌ 系統配置錯誤：缺少HF_TOKEN"}), 500
        
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # 嘗試不同的payload格式
        payloads_to_try = [
            {"data": [user_input]},  # Gradio Space 格式
            {"inputs": user_input},   # HF API 格式
            {"inputs": user_input, "parameters": {"max_length": 200, "temperature": 0.7}}
        ]
        
        success = False
        bot_reply = None
        
        for endpoint in POSSIBLE_ENDPOINTS:
            if success:
                break
                
            for payload in payloads_to_try:
                try:
                    print(f"嘗試端點: {endpoint}")
                    print(f"使用payload: {payload}")
                    
                    response = requests.post(
                        endpoint, 
                        headers=headers, 
                        json=payload,
                        timeout=30
                    )
                    
                    print(f"回應狀態碼: {response.status_code}")
                    print(f"回應內容: {response.text[:500]}...")  # 只顯示前500字符
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # 嘗試不同的回應格式解析
                        if isinstance(data, dict) and "data" in data and len(data["data"]) > 0:
                            bot_reply = data["data"][0]
                            success = True
                            print(f"成功獲得回應: {bot_reply}")
                            break
                        elif isinstance(data, list) and len(data) > 0:
                            if isinstance(data[0], dict) and "generated_text" in data[0]:
                                bot_reply = data[0]["generated_text"]
                            else:
                                bot_reply = str(data[0])
                            success = True
                            print(f"成功獲得回應: {bot_reply}")
                            break
                        elif isinstance(data, dict) and "generated_text" in data:
                            bot_reply = data["generated_text"]
                            success = True
                            print(f"成功獲得回應: {bot_reply}")
                            break
                        else:
                            print(f"未知回應格式: {data}")
                    else:
                        print(f"HTTP錯誤: {response.status_code} - {response.text}")
                        
                except requests.exceptions.RequestException as e:
                    print(f"請求錯誤 {endpoint}: {e}")
                    continue
                except Exception as e:
                    print(f"其他錯誤 {endpoint}: {e}")
                    continue
        
        if not success:
            return jsonify({"reply": "❌ 所有API端點都無法訪問，請檢查Space狀態和token"}), 500
            
    except requests.exceptions.Timeout:
        print("請求超時")
        return jsonify({"reply": "❌ 請求超時，請稍後再試"}), 500
    except Exception as e:
        print(f"系統錯誤: {e}")
        return jsonify({"reply": "❌ 系統錯誤，請稍後再試"}), 500
    
    return jsonify({"reply": bot_reply or "模型無回應"})

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "頁面不存在"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "伺服器內部錯誤"}), 500

if __name__ == "__main__":  # 修正語法錯誤
    # 生產環境配置
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
