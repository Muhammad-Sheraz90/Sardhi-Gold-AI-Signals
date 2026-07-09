import os
import requests
import pandas as pd

API_KEY = os.getenv("TWELVEDATA_API_KEY")

def get_gold_data():
    url = (
        f"https://api.twelvedata.com/time_series"
        f"?symbol=XAU/USD"
        f"&interval=15min"
        f"&outputsize=200"
        f"&apikey={API_KEY}"
    )

    response = requests.get(url)
    data = response.json()

    if "values" not in data:
        raise Exception(data)

    df = pd.DataFrame(data["values"])
    df = df.iloc[::-1]          # oldest → newest
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)

    return df
