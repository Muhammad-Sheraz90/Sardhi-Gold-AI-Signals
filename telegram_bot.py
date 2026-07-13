import requests
from config import BOT_TOKEN, CHAT_ID

def send_signal(message):
    # ٹوکن کو صاف ستھرا لنک میں شامل کرنا
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"  # اس سے ڈیزائن خوبصورت دیکھے گا
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Telegram Server Response Code: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram Send Error: {e}")
        return False
