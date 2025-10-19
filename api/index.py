import os
import requests
from flask import Flask, request
import time  # <--- 1. 匯入 time 模組

# 從環境變數讀取你的 Bot Token
TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

# 要替換的網域
TARGET_DOMAIN = "https://exhentai.org/g/"
REPLACE_DOMAIN = "https://ex.nmbyd3.top/g/"

app = Flask(__name__)

def send_reply(chat_id, text):
    """發送訊息回 Telegram"""
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    try:
        requests.post(TELEGRAM_API_URL, json=payload)
    except Exception as e:
        print(f"Error sending message: {e}")

@app.route('/', methods=['POST'])
def webhook():
    """
    Vercel 會將所有請求導向這裡
    Telegram 的 Webhook 會 POST JSON 資料到這個路由
    """
    if request.is_json:
        data = request.get_json()
        
        # 確保這是一個有效的 Telegram 訊息更新
        if 'message' in data and 'chat' in data['message'] and 'text' in data['message']:
            chat_id = data['message']['chat']['id']
            message_text = data['message']['text']
            
            # 檢查是否包含目標網域
            if TARGET_DOMAIN in message_text:
                # 執行替換
                converted_url = message_text.replace(TARGET_DOMAIN, REPLACE_DOMAIN)
                
                # 根據你的範例，確保結尾有斜線
                if not converted_url.endswith('/'):
                    converted_url += '/'
                
                # 組合你想要的豐富訊息
                reply_message = f"""沒有Ex(裡站)帳號的群友可點擊下面的連結看本

{converted_url}
"""
                
                # --- 2. 從這裡開始修改 ---
                
                # 延遲 2 秒
                try:
                    time.sleep(2)
                except Exception as e:
                    print(f"Sleep error: {e}") 

                # 回傳組合後的訊息
                send_reply(chat_id, reply_message)
                
                # --- 修改結束 ---

    # 必須回傳 200 OK，告知 Telegram 已成功接收
    return 'OK', 200

if __name__ == "__main__":
    # 這段是為了方便本地測試，Vercel 不會執行
    app.run(debug=True)
