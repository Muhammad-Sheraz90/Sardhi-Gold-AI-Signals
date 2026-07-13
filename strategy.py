import pandas as pd
import numpy as np

# انڈیکیٹرز کی سیٹنگز
EMA_FAST = 9       
EMA_SLOW = 21      
RSI_PERIOD = 14    

def calculate_indicators(df):
    df = df.copy()
    
    # EMA (Moving Average) کا حساب
    df['ema_fast'] = df['close'].ewm(span=EMA_FAST, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=EMA_SLOW, adjust=False).mean()
    
    # RSI (Relative Strength Index) کا حساب
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=RSI_PERIOD).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=RSI_PERIOD).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    return df

def check_signal(data):
    if data is None or len(data) < 30:
        return None

    df = calculate_indicators(data)
    
    # لائیو کینڈل سے پچھلی مکمل ہونے والی کینڈل چیک کریں (Index -2)
    last = df.iloc[-2]
    prev = df.iloc[-3]
    
    # بائی (BUY) کی شرط: فاسٹ موونگ ایوریج نے سلو موونگ ایوریج کو نیچے سے اوپر کراس کیا ہو
    is_buy = (prev['ema_fast'] <= prev['ema_slow']) and (last['ema_fast'] > last['ema_slow'])
    
    # سیل (SELL) کی شرط: فاسٹ موونگ ایوریج نے سلو موونگ ایوریج کو اوپر سے نیچے کراس کیا ہو
    is_sell = (prev['ema_fast'] >= prev['ema_slow']) and (last['ema_fast'] < last['ema_slow'])
    
    entry = round(last["close"], 2)
    rsi_val = round(last['rsi'], 2)
    
    if is_buy:
        sl = round(entry - 2.50, 2)  # $2.50 کا سٹاپ لاس
        tp = round(entry + 5.00, 2)  # $5.00 کا ٹیک پرافٹ
        return {
            "signal": "BUY 📈",
            "entry": entry,
            "sl": sl,
            "tp": tp,
            "rsi": rsi_val
        }
        
    elif is_sell:
        sl = round(entry + 2.50, 2)
        tp = round(entry - 5.00, 2)
        return {
            "signal": "SELL 📉",
            "entry": entry,
            "sl": sl,
            "tp": tp,
            "rsi": rsi_val
        }
        
    return None

def format_signal(signal):
    if signal is None:
        return None

    # ٹیلی گرام کے لیے خوبصورت اردو/انگریزی مکس میسج ڈیزائن
    message = f"""🔔 *NEW GOLD (XAUUSD) SIGNAL*

📊 *Type:* {signal['signal']}
🎯 *Entry:* ${signal['entry']}
🛑 *Stop Loss:* ${signal['sl']}
🎯 *Take Profit:* ${signal['tp']}
📈 *RSI Strength:* {signal['rsi']}
⏰ *Timeframe:* 5 Min

⚠️ *Educational purposes only.*"""
    return message

if __name__ == "__main__":
    print("Fast EMA & RSI Strategy Loaded Successfully")
