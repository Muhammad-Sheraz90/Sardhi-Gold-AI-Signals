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

    last = data.iloc[-1]

    # BUY
    if (
        last["EMA50"] > last["EMA200"]
        and last["close"] > last["EMA50"]
        and last["RSI"] > 55
    ):

        entry = round(last["close"], 2)

        return {
            "type": "BUY",
            "entry": entry,
            "sl": round(entry - 8, 2),
            "tp": round(entry + 16, 2),
            "confidence": 90
        }

    # SELL
    if (
        last["EMA50"] < last["EMA200"]
        and last["close"] < last["EMA50"]
        and last["RSI"] < 45
    ):

        entry = round(last["close"], 2)

        return {
            "type": "SELL",
            "entry": entry,
            "sl": round(entry + 8, 2),
            "tp": round(entry - 16, 2),
            "confidence": 90
        }

    return None
