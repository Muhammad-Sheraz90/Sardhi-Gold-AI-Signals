import requests
import pandas as pd
from datetime import datetime

def get_gold_data():
    try:
        # یاہو فنانس کا آفیشل پبلک انٹرنل لنک (گولڈ ٹکر: GC=F)
        url = "https://yahoo.com"
        
        # یہ ہیڈرز یاہو سرور کو بتاتے ہیں کہ یہ ایک حقیقی ویب براؤزر ہے، کوئی کلاؤڈ بوٹ نہیں
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            raise Exception(f"Yahoo Chart API responded with Status Code {response.status_code}")
            
        json_data = response.json()
        result = json_data["chart"]["result"][0]
        
        # ٹائم اسٹیمپ اور کینڈل اسٹک ڈیٹا نکالنا
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
        
        # خالی یا ناقص ڈیٹا کی لائنیں صاف کرنا
        df = df.dropna().reset_index(drop=True)
        
        # پائتھون ٹائم فارمیٹ (Datetime) درست کرنا
        df['datetime'] = pd.to_datetime(df['datetime'], unit='s')
        
        # تمام مالیاتی کالمز کو فلوٹ (Float) میں تبدیل کرنا
        for col in ["open", "high", "low", "close"]:
            df[col] = df[col].astype(float)
            
        return df
        
    except Exception as e:
        raise Exception(f"Yahoo Direct Stream Error: {e}")
