import time
import traceback
from config import TIMEFRAME
from market_data import get_gold_data
from strategy import check_signal, format_signal
from telegram_bot import send_signal

print("Sardhi Gold AI Bot - Main Process Started Successfully...")

# سرور آن ہوتے ہی کنکشن ٹیسٹ میسج بھیجے گا
send_signal("🚀 *Sardhi Gold AI Bot: System Fully Integrated!* \n\nYour modular bot is now active and scanning XAUUSD via Anti-Block Stream.")

last_processed_time = None

while True:
    try:
        print("Fetching market data via clean environment...")
        # market_data.py سے یاہو فنانس کا ڈیٹا لانا
        data = get_gold_data()
        
        if data is not None and not data.empty:
            # آخری کینڈل کا وقت معلوم کرنا
            current_candle_time = data['datetime'].iloc[-1]
            
            # چیک کرنا کہ اس کینڈل کا تجزیہ پہلے تو نہیں ہوا
            if current_candle_time != last_processed_time:
                print("Analyzing market metrics with strategy.py...")
                # strategy.py کے ذریعے سگنل چیک کرنا
                signal = check_signal(data)

                if signal:
                    print("Match found! Firing signal details:", signal)
                    # سگنل کو ٹیلی گرام کے خوبصورت میسج فارمیٹ میں تبدیل کرنا
                    message = format_signal(signal)
                    # telegram_bot.py کے ذریعے چینل پر بھیجنا
                    send_signal(message)
                else:
                    print("No fast signal triggers met at this timestamp.")
                
                last_processed_time = current_candle_time
            else:
                print("Candle already fully analyzed. Rest period...")

        # ہر 60 سیکنڈ بعد نئی کینڈل اپڈیٹ چیک کرے گا
        time.sleep(60)

    except Exception as e:
        print("Core loop exception caught:")
        traceback.print_exc()
        time.sleep(30)
