import os
import re
from flask import Flask, request
import time
import httpx  # 完全取代 requests

TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

EX_DOMAIN = "https://exhentai.org/g/"

TARGET_DOMAINS = {
    "E-Hentai (表站)": "https://e-hentai.org/g/",
    "Moonchan 鏡像": "https://ex.moonchan.xyz/g/",
    "方立頂 鏡像": "https://ex.fangliding.eu.org/g/"
}

app = Flask(__name__)

# 建立支援 HTTP/2 的 Client 實例
SESSION = httpx.Client(http2=True)

# 補齊現代瀏覽器（Chrome）的所有必要標頭，降低被 Cloudflare 判定為自動化腳本的機率
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "max-age=0",
    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1"
})

def send_reply(chat_id, text):
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    try:
        # Telegram API 封鎖較不嚴格，直接使用簡配 post 即可
        httpx.post(TELEGRAM_API_URL, json=payload, timeout=10.0)
    except Exception as e:
        print(f"Error sending message: {e}")

def is_gallery_available(url):
    try:
        # 發送請求，此處會自動套用上面設定的 HTTP/2 與瀏覽器標頭
        resp = SESSION.get(url, timeout=10.0)
        print(f"[Debug] URL: {url} | Status Code: {resp.status_code}")
        
        return resp.status_code == 200 and 'Gallery not found' not in resp.text
    except Exception as e:
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
                
                for name, domain in TARGET_DOMAINS.items():
                    converted_url = found_url.replace(EX_DOMAIN, domain)
                    if not converted_url.endswith('/'):
                        converted_url += '/'
                    
                    if is_gallery_available(converted_url):
                        available_links.append(f"{name}：\n{converted_url}")
                
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
