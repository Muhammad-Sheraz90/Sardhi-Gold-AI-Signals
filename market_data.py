import requests
import pandas as pd
from datetime import datetime

def get_gold_data():
    try:
        # کلاؤڈ محفوظ پبلک اے پی آئی جو گولڈ (XAU/USD) کا لائیو کینڈل ڈیٹا دیتی ہے
        url = "https://coingecko.com"
        
        headers = {
            "accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            # اگر Coingecko پر کوئی مسئلہ ہو تو متبادل اوپن سورس فید استعمال کریں
            url = "https://cryptocompare.com"
            response = requests.get(url, timeout=15)
            res_data = response.json()
            data_list = res_data["Data"]["Data"]
            df = pd.DataFrame(data_list)
            df['datetime'] = pd.to_datetime(df['time'], unit='s')
            df = df.rename(columns={"open": "open", "high": "high", "low": "low", "close": "close", "volumeto": "volume"})
        else:
            # اگر مین اے پی آئی کامیابی سے چل جائے
            json_data = response.json()
            prices = json_data["prices"]  # اس میں [timestamp, price] ہوتا ہے
            
            df = pd.DataFrame(prices, columns=["timestamp", "close"])
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # ای ایم اے اسٹریٹیجی کے لیے باقی کالمز فرضی لائیو قیمت کے برابر کرنا
            df["open"] = df["close"]
            df["high"] = df["close"]
            df["low"] = df["close"]
            df["volume"] = 1000
            
        # ڈیٹا صاف کرنا
        df = df.dropna().reset_index(drop=True)
        
        # ڈیٹا ٹائپ درست کرنا
        for col in ["open", "high", "low", "close"]:
            df[col] = df[col].astype(float)
            
        return df
        
    except Exception as e:
        raise Exception(f"Secure Cloud Data Feed Error: {e}")
