import pandas as pd

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def check_signal(data):

    last = data.iloc[-1]

    return {
        "type": "BUY",
        "entry": round(last["close"], 2)
    }
