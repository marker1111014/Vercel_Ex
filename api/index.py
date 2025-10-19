import os
import requests
from flask import Flask, request

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
                new_text = message_text.replace(TARGET_DOMAIN, REPLACE_DOMAIN)
                
                # 根據你的範例，確保結尾有斜線
                if not new_text.endswith('/'):
                    new_text += '/'
                
                # 回傳轉換後的訊息
                send_reply(chat_id, new_text)

    # 必須回傳 200 OK，告知 Telegram 已成功接收
    return 'OK', 200

if __name__ == "__main__":
    # 這段是為了方便本地測試，Vercel 不會執行
    app.run(debug=True)
