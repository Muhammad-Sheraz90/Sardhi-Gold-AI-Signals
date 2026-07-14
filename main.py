import time
from market_data import get_gold_price
from strategy import check_signal
from telegram_bot import send_signal

def main():
    print("🚀 Gold Bot Server par chal raha hai...")
    send_signal("🚀 Gold Bot successfully started on Cloud Server!")
    
    while True:
        try:
            price = get_gold_price()
            if price:
                print(f"Current Gold Price: {price}")
                signal = check_signal(price)
                
                if signal == "BUY":
                    msg = f"🟢 GOLD (XAU/USD) BUY SIGNAL\nPrice: {price}\nTime: Live"
                    send_signal(msg)
                    
            # Har 5 minute baad check karega (تاکہ سرور بلاک نہ ہو)
            time.sleep(300) 
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
