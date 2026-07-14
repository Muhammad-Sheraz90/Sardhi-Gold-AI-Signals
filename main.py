import time
from market_data import get_gold_price
from strategy import check_signal
from telegram_bot import send_signal

def main():
    print("🚀 Gold Bot Server par chal raha hai...")
    send_signal("🚀 Gold Bot successfully started on Cloud Server!")
    
    # اس سے پتہ چلے گا کہ آخری سگنل کیا تھا تاکہ بار بار میسج نہ جائے
    last_signal = None 
    
    while True:
        try:
            price = get_gold_price()
            if price:
                print(f"Current Gold Price: {price}")
                signal = check_signal(price)  # یہ "BUY"، "SELL" یا "HOLD" دے گا
                
                # اگر نیا سگنل بائے یا سیل ہے اور وہ پچھلے سگنل جیسا نہیں ہے
                if signal in ["BUY", "SELL"] and signal != last_signal:
                    emoji = "🟢" if signal == "BUY" else "🔴"
                    msg = f"{emoji} GOLD (XAU/USD) {signal} SIGNAL\nPrice: {price}\nTime: Live"
                    
                    send_signal(msg)
                    last_signal = signal  # پچھلے سگنل کو اپ ڈیٹ کر دیں
                    print(f"Signal sent to Telegram: {signal}")
                
                elif signal == "HOLD":
                    # اگر مارکیٹ نارمل ہو جائے تو پرانا سگنل ری سیٹ کر دیں
                    last_signal = None

            # ہر 5 منٹ بعد مارکیٹ چیک کرے گا (300 سیکنڈز)
            time.sleep(300) 
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
