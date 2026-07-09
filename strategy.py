import pandas as pd

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def check_signal(data):

    if len(data) < 200:
        return None

    data["EMA50"] = ema(data["close"], 50)
    data["EMA200"] = ema(data["close"], 200)

    last = data.iloc[-1]
    prev = data.iloc[-2]

    # BUY Cross
    if (
        prev["EMA50"] <= prev["EMA200"] and
        last["EMA50"] > last["EMA200"]
    ):
        return {
            "type": "BUY",
            "entry": round(last["close"], 2),
            "sl": round(last["close"] - 10, 2),
            "tp": round(last["close"] + 20, 2),
            "confidence": 85
        }

    # SELL Cross
    if (
        prev["EMA50"] >= prev["EMA200"] and
        last["EMA50"] < last["EMA200"]
    ):
        return {
            "type": "SELL",
            "entry": round(last["close"], 2),
            "sl": round(last["close"] + 10, 2),
            "tp": round(last["close"] - 20, 2),
            "confidence": 85
        }

    return None
