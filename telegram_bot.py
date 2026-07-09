import requests
from config import BOT_TOKEN, CHAT_ID

def send_signal(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    response = requests.post(url, data=payload)

    print(response.status_code)
    print(response.text)
    print(response.status_code)
    print(response.text)
    print(response.json())
    print("BOT_TOKEN =", BOT_TOKEN)
    print("CHAT_ID =", CHAT_ID)
    return response.status_code == 200
