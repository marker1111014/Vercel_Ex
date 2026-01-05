import os
import requests
import re
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
            
            # --- 修改開始 ---
            
            # 定義 ExHentai 網址的正規表達式格式
            # 解釋：尋找 https://exhentai.org/g/數字/英數混合/
            pattern = r"https://exhentai\.org/g/\d+/[a-z0-9]+"
            
            # 使用 re.search 搜尋訊息中是否包含符合格式的網址
            match = re.search(pattern, message_text)
            
            if match:
                # 抓取到的純網址 (例如 https://exhentai.org/g/3710200/f978f40d69)
                found_url = match.group(0)
                
                # 執行網址替換 (只針對抓到的網址進行替換)
                converted_url = found_url.replace(TARGET_DOMAIN, REPLACE_DOMAIN)
                
                # 確保結尾有斜線 (這邏輯保留)
                if not converted_url.endswith('/'):
                    converted_url += '/'
                
                # 組合訊息
                reply_message = f"""沒有Ex(裡站)帳號的群友
可點擊下方的連結看上面的本

{converted_url}
"""
                
                # 延遲處理
                try:
                    time.sleep(2)
                except Exception as e:
                    print(f"Sleep error: {e}") 

                # 發送回覆
                send_reply(chat_id, reply_message)
                
            # --- 修改結束 ---

    return 'OK', 200

if __name__ == "__main__":
    # 這段是為了方便本地測試，Vercel 不會執行
    app.run(debug=True)



