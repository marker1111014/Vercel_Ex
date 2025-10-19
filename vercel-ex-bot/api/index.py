import os
import requests
from flask import Flask, request

# --- 環境變數與常數 ---
# Vercel 會從你設定的 "Environment Variables" 讀取
TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

TARGET_DOMAIN = "https://exhentai.org/g/"
REPLACE_DOMAIN = "https://ex.nmbyd3.top/g/"


# --- Flask 應用程式實例 ---
# Vercel 需要這個 'app' 變數，且必須在全域範圍 (不能縮排)
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

# --- Webhook 路由 ---
# 這是 Vercel Function 的進入點
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

# 注意：Vercel 會忽略 if __name__ == "__main__": 區塊
# 所以 app.run() 不會在這裡執行，這是正常的
