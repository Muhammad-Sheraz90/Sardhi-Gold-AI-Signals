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
def detect_liquidity(data):

    data["BuyLiquidity"] = False
    data["SellLiquidity"] = False

    previous_high = data["SwingHigh"].shift(1)
    previous_low = data["SwingLow"].shift(1)

    for i in range(1, len(data)):

        if pd.isna(previous_high.iloc[i]) or pd.isna(previous_low.iloc[i]):
            continue

        # Buy-side Liquidity Sweep
        if (
            data["high"].iloc[i] > previous_high.iloc[i]
            and
            data["close"].iloc[i] < previous_high.iloc[i]
        ):
            data.loc[data.index[i], "BuyLiquidity"] = True

        # Sell-side Liquidity Sweep
        if (
            data["low"].iloc[i] < previous_low.iloc[i]
            and
            data["close"].iloc[i] > previous_low.iloc[i]
        ):
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


def detect_fvg(data):

    data["BullishFVG"] = False
    data["BearishFVG"] = False

    data["FVGHigh"] = np.nan
    data["FVGLow"] = np.nan

    for i in range(2, len(data)):

        if data["low"].iloc[i] > data["high"].iloc[i-2]:

            data.loc[data.index[i], "BullishFVG"] = True
            data.loc[data.index[i], "FVGLow"] = data["high"].iloc[i-2]
            data.loc[data.index[i], "FVGHigh"] = data["low"].iloc[i]

        if data["high"].iloc[i] < data["low"].iloc[i-2]:

            data.loc[data.index[i], "BearishFVG"] = True
            data.loc[data.index[i], "FVGHigh"] = data["low"].iloc[i-2]
            data.loc[data.index[i], "FVGLow"] = data["high"].iloc[i]

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

signal = None

for i in range(len(data) - 20, len(data) - 1):

    last = data.iloc[i]

    if buy_setup(last):
        signal = create_signal(last, "BUY")

    elif sell_setup(last):
        signal = create_signal(last, "SELL")

if signal:
    return signal

last = data.iloc[-2]

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
