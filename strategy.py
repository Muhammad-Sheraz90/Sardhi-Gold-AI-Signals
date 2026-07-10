import pandas as pd

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def rsi(series, period=14):
    delta = series.diff()   


    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

    rs = gain / loss
    return 100 - (100 / (1 + rs))
def atr(data, period=14):
    high_low = data["high"] - data["low"]
    high_close = (data["high"] - data["close"].shift()).abs()
    low_close = (data["low"] - data["close"].shift()).abs()

    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def check_signal(data):
    

    if len(data) < 200:
        return None

    data["EMA50"] = ema(data["close"], 50)
    data["EMA200"] = ema(data["close"], 200)
    data["RSI"] = rsi(data["close"])
    data["ATR"] = atr(data)
    data["SwingHigh"] = data["high"].rolling(5).max()
    data["SwingLow"] = data["low"].rolling(5).min()
    data["BOS_BUY"] = data["close"] > data["SwingHigh"].shift(1)
    data["BOS_SELL"] = data["close"] < data["SwingLow"].shift(1)
    data["LiquidityBuy"] = (data["low"] < data["SwingLow"].shift(1)) & (data["close"] > data["SwingLow"].shift(1))
    data["LiquiditySell"] = (data["high"] > data["SwingHigh"].shift(1)) & (data["close"] < data["SwingHigh"].shift(1))

    last = data.iloc[-1]
    print("LiquidityBuy:", last["LiquidityBuy"])
    print("LiquiditySell:", last["LiquiditySell"])
    print("BOS_BUY:", last["BOS_BUY"])
    print("BOS_SELL:", last["BOS_SELL"])
    print("Close:", last["close"])
    print("EMA50:", last["EMA50"])
    print("EMA200:", last["EMA200"])
    print("RSI:", last["RSI"])
    print("ATR:", last["ATR"])

        # BUY
    if (
    
        last["EMA50"] > last["EMA200"]
        and last["close"] > last["EMA50"]
        and 55 < last["RSI"] < 70
        and last["ATR"] > 5
        and last["BOS_BUY"]
    ):

        entry = float(round(last["close"], 2))
        sl = round(last["SwingLow"], 2)
        tp = round(entry + ((entry - sl) * 2), 2)

        return {
            "type": "BUY",
            "entry": entry,
            "sl": sl,
            "tp": tp,
            "confidence": 92
        }

    # SELL
    if (
        last["EMA50"] < last["EMA200"]
        and last["close"] < last["EMA50"]
        and 30 < last["RSI"] < 45
        and last["ATR"] > 5
        and last["BOS_SELL"]
    ):

        entry = float(round(last["close"], 2))
        sl = round(last["SwingHigh"], 2)
        tp = round(entry - ((sl - entry) * 2), 2)

        return {
            "type": "SELL",
            "entry": entry,
            "sl": sl,
            "tp": tp,
            "confidence": 92
        }

    return None
