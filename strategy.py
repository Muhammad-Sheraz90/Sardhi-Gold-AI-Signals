"""
Sardhi Gold AI V2
strategy.py (Starter Version)

NOTE:
This file is a merged starter based on the strategy discussed in chat.
It is intended as a foundation and should be integrated with the rest of
the project (market_data.py, main.py, telegram_bot.py).
"""

import pandas as pd


def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()


def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def atr(data, period=14):
    high_low = data["high"] - data["low"]
    high_close = (data["high"] - data["close"].shift(1)).abs()
    low_close = (data["low"] - data["close"].shift(1)).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.ewm(alpha=1/period, adjust=False).mean()


def prepare_data(data):
    data = data.copy()
    data["EMA50"] = ema(data["close"], 50)
    data["EMA200"] = ema(data["close"], 200)
    data["RSI"] = rsi(data["close"], 14)
    data["ATR"] = atr(data, 14)
    data.dropna(inplace=True)
    return data


def prepare_structure(data, lookback=20):
    data = data.copy()
    data["SwingHigh"] = data["high"].rolling(lookback).max().shift(1)
    data["SwingLow"] = data["low"].rolling(lookback).min().shift(1)

    buffer = data["ATR"] * 0.10
    data["BullishBOS"] = data["close"] > (data["SwingHigh"] + buffer)
    data["BearishBOS"] = data["close"] < (data["SwingLow"] - buffer)

    rng = (data["high"] - data["low"]).replace(0, 1e-6)
    body = (data["close"] - data["open"]).abs()
    ratio = body / rng

    data["LiquidityBuy"] = (
        (data["low"] < data["SwingLow"])
        & (data["close"] > data["SwingLow"])
        & (ratio >= 0.40)
    )

    data["LiquiditySell"] = (
        (data["high"] > data["SwingHigh"])
        & (data["close"] < data["SwingHigh"])
        & (ratio >= 0.40)
    )
    return data


def check_signal(data):
    if data is None or len(data) < 220:
        return None

    data = prepare_data(data)
    data = prepare_structure(data)

    last = data.iloc[-2]

    buy = (
        last["EMA50"] > last["EMA200"]
        and last["BullishBOS"]
        and last["LiquidityBuy"]
        and 50 <= last["RSI"] <= 70
    )

    sell = (
        last["EMA50"] < last["EMA200"]
        and last["BearishBOS"]
        and last["LiquiditySell"]
        and 30 <= last["RSI"] <= 50
    )

    if buy:
        return {"type": "BUY", "entry": round(last["close"],2)}

    if sell:
        return {"type": "SELL", "entry": round(last["close"],2)}

    return None
