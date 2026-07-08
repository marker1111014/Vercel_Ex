import os
import requests
import re
from flask import Flask, request
import time

TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

EX_DOMAIN = "https://exhentai.org/g/"

# 新增：將所有需要測試的站點與名稱定義在此處，方便日後新增或刪除
TARGET_DOMAINS = {
    "E-Hentai (表站)": "https://e-hentai.org/g/",
    "Moonchan 鏡像": "https://ex.moonchan.xyz/g/",
    "方立頂 鏡像": "https://ex.fangliding.eu.org/g/"
}

app = Flask(__name__)

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

def send_reply(chat_id, text):
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    try:
        requests.post(TELEGRAM_API_URL, json=payload)
    except Exception as e:
        print(f"Error sending message: {e}")

def is_gallery_available(url):
    try:
        resp = SESSION.get(url, timeout=10)
        # 新增這行：在後台印出實際收到的 HTTP 狀態碼
        print(f"[Debug] URL: {url} | Status Code: {resp.status_code}")
        
        return resp.status_code == 200 and 'Gallery not found' not in resp.text
    except Exception as e:
        # 如果發生連線錯誤、SSL 錯誤或連線逾時，會印在這裡
        print(f"Error checking gallery on {url}: {e}")
        return False

@app.route('/', methods=['POST'])
def webhook():
    if request.is_json:
        data = request.get_json()
        
        if 'message' in data and 'chat' in data['message'] and 'text' in data['message']:
            chat_id = data['message']['chat']['id']
            message_text = data['message']['text']
            
            pattern = r"https://exhentai\.org/g/\d+/[a-z0-9]+"
            match = re.search(pattern, message_text)
            
            if match:
                found_url = match.group(0)
                available_links = []
                
                # 依序檢查每個站點
                for name, domain in TARGET_DOMAINS.items():
                    converted_url = found_url.replace(EX_DOMAIN, domain)
                    if not converted_url.endswith('/'):
                        converted_url += '/'
                    
                    if is_gallery_available(converted_url):
                        available_links.append(f"{name}：\n{converted_url}")
                
                # 如果有任何一個站點可用，則回傳可用清單
                if available_links:
                    links_text = "\n\n".join(available_links)
                    reply_message = f"沒有Ex(裡站)帳號的群友\n可點擊下方的連結看上面的本\n\n{links_text}"
                else:
                    reply_message = "這是ex站專屬連結，目前測試的表站與鏡像站皆無法存取（可能已掛點或受到防爬蟲阻擋）。"
                
                try:
                    time.sleep(2)
                except Exception as e:
                    print(f"Sleep error: {e}")
                
                send_reply(chat_id, reply_message)
    
    return 'OK', 200

if __name__ == "__main__":
    app.run(debug=True)
