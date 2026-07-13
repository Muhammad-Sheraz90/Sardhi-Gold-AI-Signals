import os
import time
import traceback
import requests
import pandas as pd
from datetime import datetime

# --- کنفیگریشن (Configuration) ---
BOT_TOKEN = "8725455662:AAFbNrhovW6Mh_gT0JA9E2nFJxj2BCTUX-8"
CHAT_ID = "YOUR_CHAT_ID" 7358356587

SYMBOL = "XAU/USD"
INTERVAL = "5min"
EMA_FAST = 9       # تیز موونگ ایوریج
EMA_SLOW = 21      # آہستہ موونگ ایوریج
RSI_PERIOD = 14    # آر ایس آئی پیریڈ

print("Sardhi Gold AI Bot (Fast Mode) Started...")

# ==========================================================
# ٹیلی گرام الرٹ فنکشن
# ==========================================================
def send_signal(message):
    url = "https://telegram.org"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("Telegram alert sent successfully.")
        else:
            print(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        print(f"Telegram Error: {e}")

# ==========================================================
# مارکیٹ ڈیٹا حاصل کرنا
# ==========================================================
def get_gold_data():
    # TwelveData API Key
    api_key = os.getenv("TWELVEDATA_API_KEY", "YOUR_TWELVEDATA_API_KEY")
    url = (
        "https://twelvedata.com"
        f"?symbol={SYMBOL}"
        f"&interval={INTERVAL}"
        "&outputsize=100"
        "&format=JSON"
        "&timezone=UTC"
        f"&apikey={api_key}"
    )
    response = requests.get(url, timeout=30)
    data = response.json()

    if "values" not in data:
        raise Exception(f"API Error: {data}")

    df = pd.DataFrame(data["values"])
    df = df.rename(columns={"datetime": "datetime"})
    df["datetime"] = pd.to_datetime(df["datetime"])

    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)

    df = df.sort_values("datetime").reset_index(drop=True)
    return df

# ==========================================================
# انڈیکیٹرز کا حساب (EMA & RSI)
# ==========================================================
def calculate_indicators(df):
    df = df.copy()
    # EMA کا حساب
    df['ema_fast'] = df['close'].ewm(span=EMA_FAST, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=EMA_SLOW, adjust=False).mean()
    
    # RSI کا حساب
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=RSI_PERIOD).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=RSI_PERIOD).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    return df

# ==========================================================
# سگنل کی جانچ (Fast Strategy)
# ==========================================================
def check_signal(data):
    if data is None or len(data) < 30:
        return None

    df = calculate_indicators(data)
    
    # آخری مکمل ہونے والی کینڈل (index -2)
    last = df.iloc[-2]
    prev = df.iloc[-3]
    
    # بائی (BUY) کی شرط: فاسٹ ایوریج نے سلو ایوریج کو نیچے سے اوپر کراس کیا ہو
    is_buy = (prev['ema_fast'] <= prev['ema_slow']) and (last['ema_fast'] > last['ema_slow'])
    
    # سیل (SELL) کی شرط: فاسٹ ایوریج نے سلو ایوریج کو اوپر سے نیچے کراس کیا ہو
    is_sell = (prev['ema_fast'] >= prev['ema_slow']) and (last['ema_fast'] < last['ema_slow'])
    
    entry = round(last["close"], 2)
    
    if is_buy:
        sl = round(entry - 2.50, 2)  # $2.50 کا فکسڈ سٹاپ لاس
        tp = round(entry + 5.00, 2)  # $5.00 کا ٹیک پرافٹ (1:2 ریسک ریوارڈ)
        return {"signal": "BUY 📈", "entry": entry, "sl": sl, "tp": tp, "rsi": round(last['rsi'], 2)}
        
    elif is_sell:
        sl = round(entry + 2.50, 2)
        tp = round(entry - 5.00, 2)
        return {"signal": "SELL 📉", "entry": entry, "sl": sl, "tp": tp, "rsi": round(last['rsi'], 2)}
        
    return None

# ==========================================================
# مین رننگ لوپ (Main Execution Loop)
# ==========================================================
last_processed_time = None

# جیسے ہی سرور آن ہوگا، یہ کنکشن ٹیسٹ میسج چینل پر بھیج دے گا
send_signal("🚀 *Sardhi Gold AI Bot: Fast Mode Activated!* \n\nScanning XAUUSD on 5-Minute Chart...")

while True:
    try:
        print("Getting market data...")
        data = get_gold_data()
        
        if not data.empty:
            current_candle_time = data['datetime'].iloc[-1]
            
            if current_candle_time != last_processed_time:
                print("Checking signal...")
                signal = check_signal(data)

                if signal:
                    print("Signal found:", signal)
                    message = f"""🔔 *NEW GOLD (XAUUSD) SIGNAL*

📊 *Type:* {signal['signal']}
🎯 *Entry:* ${signal['entry']}
🛑 *Stop Loss:* ${signal['sl']}
🎯 *Take Profit:* ${signal['tp']}
📈 *RSI Strength:* {signal['rsi']}
⏰ *Timeframe:* 5 Min

⚠️ *Educational purposes only.*"""
                    
                    send_signal(message)
                else:
                    print("No fast signal found at this candle.")
                
                last_processed_time = current_candle_time
            else:
                print("Candle already analyzed. Waiting for next 5m candle...")

        time.sleep(30)  # ہر 30 سیکنڈ بعد کینڈل اپڈیٹ چیک کرے گا

except Exception as e:
        print("An error occurred:")
        traceback.print_exc()
        time.sleep(30)
