import yfinance as yf
import pandas as pd

def get_gold_data():

    symbol = "GC=F"

    data = yf.download(
        symbol,
        period="5d",
        interval="15m",
        progress=False
    )

    data = data.dropna()

    return data
