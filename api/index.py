import os
import requests
import re
from flask import Flask, request
import time

TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

# # 舊的鏡像站取代功能（保留備用）
# TARGET_DOMAIN = "https://exhentai.org/g/"
# REPLACE_DOMAIN = "https://e.810114.xyz/g/"

EX_DOMAIN = "https://exhentai.org/g/"
EH_DOMAIN = "https://e-hentai.org/g/"

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
        return resp.status_code == 200 and 'Gallery not found' not in resp.text
    except Exception as e:
        print(f"Error checking gallery: {e}")
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
                eh_url = found_url.replace(EX_DOMAIN, EH_DOMAIN)
                if not eh_url.endswith('/'):
                    eh_url += '/'
                
                # # 舊的鏡像站取代邏輯
                # converted_url = found_url.replace(TARGET_DOMAIN, REPLACE_DOMAIN)
                # if not converted_url.endswith('/'):
                #     converted_url += '/'
                # reply_message = f"""沒有Ex(裡站)帳號的群友\n可點擊下方的連結看上面的本\n\n{converted_url}\n"""
                
                if is_gallery_available(eh_url):
                    reply_message = f"""沒有Ex(裡站)帳號的群友
可點擊下方的連結看上面的本

{eh_url}
"""
                else:
                    reply_message = "這是ex站專屬連結，鏡像站目前已掛點"
                
                try:
                    time.sleep(2)
                except Exception as e:
                    print(f"Sleep error: {e}")
                
                send_reply(chat_id, reply_message)
    
    return 'OK', 200

if __name__ == "__main__":
    app.run(debug=True)



