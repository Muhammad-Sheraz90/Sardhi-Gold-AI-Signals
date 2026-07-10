from telegram_bot import send_signal
from market_data import get_gold_data
from strategy import check_signal
import time
import traceback

print("Sardhi Gold AI Bot Started...")

while True:
    try:
        print("Getting market data...")
        data = get_gold_data()

        print("Checking signal...")
        signal = check_signal(data)

        print(signal)

        if signal is None:
            print("No signal found.")
        else:
            print("Signal found:", signal)

        print(data.tail())

        if signal:
            message = f"""
🟢 Sardhi Gold AI Signal

📈 Pair: XAUUSD

✅ Signal: {signal['type']}

🎯 Entry: {signal['entry']}

🛑 Stop Loss: {signal['sl']}

💰 Take Profit: {signal['tp']}

🔥 Confidence: {signal['confidence']}%

⚠️ Educational purposes only.
"""

            send_signal(message)

        # Check again after 5 minutes
        time.sleep(300)

    except Exception as e:
        traceback.print_exc()
        time.sleep(60)
