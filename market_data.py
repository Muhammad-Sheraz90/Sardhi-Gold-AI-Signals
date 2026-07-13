import requests
import pandas as pd
from datetime import datetime
from config import SYMBOL, TIMEFRAME

def get_gold_data():
    try:
        # یاہو فنانس کا تیز ترین لنک (بغیر کسی اے پی آئی کی کے)
        url = "https://yahoo.com"

        
        # یہ ہیڈر ویب سائٹ کو بتاتا ہے کہ یہ ایک نارمل موبائل/کمپیوٹر براؤزر ہے
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            raise Exception(f"Yahoo Server responded with Status {response.status_code}")
            
        json_data = response.json()
        result = json_data["chart"]["result"][0]
        
        # ڈیٹا نکالنا اور ترتیب دینا
        timestamps = result["timestamp"]
        indicators = result["indicators"]["quote"][0]
        
        df = pd.DataFrame({
            "datetime": timestamps,
            "open": indicators["open"],
            "high": indicators["high"],
            "low": indicators["low"],
            "close": indicators["close"],
            "volume": indicators["volume"]
        })
        
        # خالی لائنیں صاف کرنا اور ٹائم فارمیٹ درست کرنا
        df = df.dropna().reset_index(drop=True)
        df['datetime'] = pd.to_datetime(df['datetime'], unit='s')
        
        # ڈیٹا ٹائپس درست کرنا
        for col in ["open", "high", "low", "close"]:
            df[col] = df[col].astype(float)
            
        return df
        
    except Exception as e:
        raise Exception(f"Anti-Block Market Data Error: {e}")
