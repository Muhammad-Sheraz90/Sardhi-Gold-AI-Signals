# ==========================================================
# Sardhi Gold AI V3
# ICT Strategy
# ==========================================================

import pandas as pd
import numpy as np


SWING_LOOKBACK = 5
RR = 2.0


def detect_swings(data):

    data = data.copy()

    data["SwingHigh"] = np.nan
    data["SwingLow"] = np.nan

    for i in range(SWING_LOOKBACK, len(data) - SWING_LOOKBACK):

        if data["high"].iloc[i] == max(
            data["high"].iloc[i-SWING_LOOKBACK:i+SWING_LOOKBACK+1]
        ):
            data.loc[data.index[i], "SwingHigh"] = data["high"].iloc[i]

        if data["low"].iloc[i] == min(
            data["low"].iloc[i-SWING_LOOKBACK:i+SWING_LOOKBACK+1]
        ):
            data.loc[data.index[i], "SwingLow"] = data["low"].iloc[i]

    data["SwingHigh"] = data["SwingHigh"].ffill()
    data["SwingLow"] = data["SwingLow"].ffill()

    return data
# ==========================================================
# LIQUIDITY SWEEP (ICT)
# ==========================================================

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

        # BUY SIDE LIQUIDITY SWEEP
        if high > swing_high and close < swing_high:
            data.loc[data.index[i], "BuyLiquidity"] = True

        # SELL SIDE LIQUIDITY SWEEP
        if low < swing_low and close > swing_low:
            data.loc[data.index[i], "SellLiquidity"] = True

    return data




def detect_choch(data):

    data["BullishCHOCH"] = False
    data["BearishCHOCH"] = False

    for i in range(1, len(data)):

        if data["close"].iloc[i] > data["high"].iloc[i-1]:
            data.loc[data.index[i], "BullishCHOCH"] = True

        if data["close"].iloc[i] < data["low"].iloc[i-1]:
            data.loc[data.index[i], "BearishCHOCH"] = True

    return data


# ==========================================================
# FAIR VALUE GAP (ICT)
# ==========================================================

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

        # Bullish FVG
        if low > high_2:

            gap = low - high_2

            if gap > 0.02:

                data.loc[data.index[i], "BullishFVG"] = True
                data.loc[data.index[i], "FVGLow"] = high_2
                data.loc[data.index[i], "FVGHigh"] = low

        # Bearish FVG
        elif high < low_2:

            gap = low_2 - high

            if gap > 0.02:

                data.loc[data.index[i], "BearishFVG"] = True
                data.loc[data.index[i], "FVGHigh"] = low_2
                data.loc[data.index[i], "FVGLow"] = high

    return data
    # ==========================================================
# PREPARE ICT
# ==========================================================

def prepare_ict(data):

    data = detect_swings(data)
    data = detect_liquidity(data)
    data = detect_choch(data)
    data = detect_fvg(data)

    return data


# ==========================================================
# BUY SETUP
# ==========================================================

def buy_setup(last):

    return (
        last["SellLiquidity"]
        and
        last["BullishCHOCH"]
        and
        last["BullishFVG"]
    )


# ==========================================================
# SELL SETUP
# ==========================================================

def sell_setup(last):

    return (
        last["BuyLiquidity"]
        and
        last["BearishCHOCH"]
        and
        last["BearishFVG"]
    )


# ==========================================================
# STOP LOSS
# ==========================================================

def stop_loss(last, signal):

    if signal == "BUY":
        return round(last["low"], 2)

    return round(last["high"], 2)


# ==========================================================
# TAKE PROFIT
# ==========================================================

def take_profit(entry, sl, signal):

    risk = abs(entry - sl)

    if signal == "BUY":
        tp = entry + (risk * RR)

    else:
        tp = entry - (risk * RR)

    return round(tp, 2)


# ==========================================================
# CREATE SIGNAL
# ==========================================================

def create_signal(last, signal):

    entry = round(last["close"], 2)

    sl = stop_loss(last, signal)

    tp = take_profit(entry, sl, signal)

    return {

        "signal": signal,

        "entry": entry,

        "sl": sl,

        "tp": tp

    }
    # ==========================================================
# CHECK SIGNAL
# ==========================================================

def check_signal(data):

    if data is None:
        return None

    if len(data) < 50:
        return None

    data = prepare_ict(data)

    signal = None

    for i in range(max(0, len(data) - 20), len(data) - 1):

        last = data.iloc[i]
        print("--------------")
        print("Index:", i)
        print("BuyLiquidity:", last["BuyLiquidity"])
        print("SellLiquidity:", last["SellLiquidity"])
        print("BullishCHOCH:", last["BullishCHOCH"])
        print("BearishCHOCH:", last["BearishCHOCH"])
        print("BullishFVG:", last["BullishFVG"])
        print("BearishFVG:", last["BearishFVG"])

        if buy_setup(last):
            signal = create_signal(last, "BUY")

        elif sell_setup(last):
            signal = create_signal(last, "SELL")

    if signal:
        return signal

    return None


# ==========================================================
# TELEGRAM MESSAGE
# ==========================================================

def format_signal(signal):

    if signal is None:
        return None

    message = f"""
🟢 Sardhi Gold AI V3

Signal : {signal['signal']}

Entry : {signal['entry']}

Stop Loss : {signal['sl']}

Take Profit : {signal['tp']}

Strategy :
ICT Liquidity Sweep
+
CHOCH
+
FVG
"""

    return message


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    print("ICT Strategy Loaded Successfully")
