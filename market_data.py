import requests
import pandas as pd
from config import TWELVEDATA_API_KEY

SYMBOL = "XAU/USD"
INTERVAL = "15min"


def get_gold_data():

    url = (
        "https://api.twelvedata.com/time_series"
        f"?symbol={SYMBOL}"
        f"&interval={INTERVAL}"
        "&outputsize=500"
        "&timezone=UTC"
        f"&apikey={TWELVEDATA_API_KEY}"
    )

    response = requests.get(url, timeout=30)
    data = response.json()

    if "values" not in data:
        raise Exception(data)

    df = pd.DataFrame(data["values"])

    df = df.rename(
        columns={
            "datetime": "datetime",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume",
        }
    )

    df["datetime"] = pd.to_datetime(df["datetime"])

    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)

    df = df.sort_values("datetime").reset_index(drop=True)

    return df
