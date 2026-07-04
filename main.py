from telegram_bot import send_signal
from market_data import get_market_data
from strategy import check_signal
import time

print("Sardhi Gold AI Bot Started...")

while True:
    try:
        data = get_market_data()
        signal = check_signal(data)

        if signal:
            message = f"""
🟢 Sardhi Gold AI Signal

Pair: XAUUSD
Signal: {signal['type']}
Entry: {signal['entry']}

⚠️ Educational purposes only.
"""
            send_signal(message)

        time.sleep(300)   # ہر 5 منٹ بعد چیک کرے گا

    except Exception as e:
        print(e)
        time.sleep(60)
