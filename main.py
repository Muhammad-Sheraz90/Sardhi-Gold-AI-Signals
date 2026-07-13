import os
import time
import traceback
import requests
import pandas as pd
import numpy as np
from datetime import datetime

# --- کنفیگریشن (Configuration) ---
# اگر آپ کلاؤڈ پر چلا رہے ہیں تو Environment Variables استعمال کریں، ورنہ نیچے براہ راست اپنی آئی ڈیز لکھ دیں
BOT_TOKEN = "8725455662:AAFbNrhovW6Mh_gT0JA9E2nFJxj2BCTUX-8"
CHAT_ID = "7358356587"

TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY", "YOUR_TWELVEDATA_API_KEY")

SYMBOL = "XAU/USD"
INTERVAL = "5min"
SWING_LOOKBACK = 5
RR = 2.0

print("Sardhi Gold AI Bot Started...")


# ==========================================================
# ٹیلی گرام الرٹ
# ==========================================================
def send_signal(message):
    # ٹوکن کو صاف کرنا تاکہ کوئی فالتو لفظ یا اسپیس نہ رہے
    clean_token = str(BOT_TOKEN).strip()
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
    url = (
        "https://api.twelvedata.com/time_series"
        f"?symbol={SYMBOL}"
        f"&interval={INTERVAL}"
        "&outputsize=500"
        "&format=JSON"
        "&timezone=UTC"
        f"&apikey={TWELVEDATA_API_KEY}"
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
# ICT اسٹریٹیجی کے انڈیکیٹرز
# ==========================================================
def detect_swings(data):
    data = data.copy()
    data["SwingHigh"] = np.nan
    data["SwingLow"] = np.nan

    for i in range(SWING_LOOKBACK, len(data) - SWING_LOOKBACK):
        if data["high"].iloc[i] == max(data["high"].iloc[i-SWING_LOOKBACK:i+SWING_LOOKBACK+1]):
            data.loc[data.index[i], "SwingHigh"] = data["high"].iloc[i]
        if data["low"].iloc[i] == min(data["low"].iloc[i-SWING_LOOKBACK:i+SWING_LOOKBACK+1]):
            data.loc[data.index[i], "SwingLow"] = data["low"].iloc[i]

    data["SwingHigh"] = data["SwingHigh"].ffill()
    data["SwingLow"] = data["SwingLow"].ffill()
    return data

def detect_liquidity(data):
    data = data.copy()
    data["BuyLiquidity"] = False
    data["SellLiquidity"] = False

    for i in range(10, len(data)):
        swing_high = data["high"].iloc[i-10:i].max()
        swing_low = data["low"].iloc[i-10:i].min()
        high = data["high"].iloc[i]
        low = data["low"].iloc[i]
        close = data["close"].iloc[i]

        if high > swing_high and close < swing_high:
            data.loc[data.index[i], "BuyLiquidity"] = True
        if low < swing_low and close > swing_low:
            data.loc[data.index[i], "SellLiquidity"] = True
    return data

def detect_choch(data):
    data = data.copy()
    data["BullishCHOCH"] = False
    data["BearishCHOCH"] = False

    for i in range(1, len(data)):
        if data["close"].iloc[i] > data["high"].iloc[i-1]:
            data.loc[data.index[i], "BullishCHOCH"] = True
        if data["close"].iloc[i] < data["low"].iloc[i-1]:
            data.loc[data.index[i], "BearishCHOCH"] = True
    return data

def detect_fvg(data):
    data = data.copy()
    data["BullishFVG"] = False
    data["BearishFVG"] = False
    data["FVGHigh"] = np.nan
    data["FVGLow"] = np.nan

    for i in range(2, len(data)):
        high_2 = data["high"].iloc[i-2]
        low_2 = data["low"].iloc[i-2]
        high = data["high"].iloc[i]
        low = data["low"].iloc[i]

        if low > high_2:
            gap = low - high_2
            if gap > 0.02:
                data.loc[data.index[i], "BullishFVG"] = True
                data.loc[data.index[i], "FVGLow"] = high_2
                data.loc[data.index[i], "FVGHigh"] = low
        elif high < low_2:
            gap = low_2 - high
            if gap > 0.02:
                data.loc[data.index[i], "BearishFVG"] = True
                data.loc[data.index[i], "FVGHigh"] = low_2
                data.loc[data.index[i], "FVGLow"] = high
    return data

def prepare_ict(data):
    data = detect_swings(data)
    data = detect_liquidity(data)
    data = detect_choch(data)
    data = detect_fvg(data)
    return data

# ==========================================================
# سگنل کی جانچ اور تخلیق (چیکنگ لوپ مکمل کر دیا گیا ہے)
# ==========================================================
def check_signal(data):
    if data is None or len(data) < 50:
        return None

    data = prepare_ict(data)
    
    # صرف آخری مکمل کینڈل چیک کریں تاکہ پرانے بار بار سگنل نہ آئیں
    last = data.iloc[-2] 
    
    # سگنل لاجک چیک کرنا
    is_buy = last["SellLiquidity"] and last["BullishCHOCH"]
    is_sell = last["BuyLiquidity"] and last["BearishCHOCH"]
    
    if is_buy:
        entry = round(last["close"], 2)
        sl = round(last["low"], 2)
        risk = abs(entry - sl)
        tp = round(entry + (risk * RR), 2)
        return {"signal": "BUY", "entry": entry, "sl": sl, "tp": tp}
        
    elif is_sell:
        entry = round(last["close"], 2)
        sl = round(last["high"], 2)
        risk = abs(entry - sl)
        tp = round(entry - (risk * RR), 2)
        return {"signal": "SELL", "entry": entry, "sl": sl, "tp": tp}
        
    return None

# ==========================================================
# مین رننگ لوپ (Main Execution Loop)
# ==========================================================
last_processed_time = None
send_signal("🚀 *Sardhi Gold AI Bot: Connection Test Successful!*")

while True:
    try:
        print("Getting market data...")
        data = get_gold_data()
        
        if not data.empty:
            current_candle_time = data['datetime'].iloc[-2]
            
            # چیک کریں کہ موجودہ کینڈل کا سگنل پہلے پروسیس تو نہیں ہوا
            if current_candle_time != last_processed_time:
                print("Checking signal...")
                signal = check_signal(data)

                if signal:
                    print("Signal found:", signal)
                    message = f"""🟢 *Sardhi Gold AI Signal*

📈 Pair: XAUUSD
✅ Signal: {signal['signal']}
🎯 Entry: {signal['entry']}
🛑 Stop Loss: {signal['sl']}
💰 Take Profit: {signal['tp']}
🔥 Strategy: ICT Smart Money

⚠️ Educational purposes only."""
                    
                    send_signal(message)
                else:
                    print("No signal found at this candle.")
                
                last_processed_time = current_candle_time
            else:
                print("Candle already analyzed. Waiting for next interval...")

        # ہر 1 منٹ بعد چیک کرے گا کہ نئی 5 منٹ کی کینڈل بنی یا نہیں
        time.sleep(60)

    except Exception as e:
        print("An error occurred:")
        traceback.print_exc()
        time.sleep(30)
        
