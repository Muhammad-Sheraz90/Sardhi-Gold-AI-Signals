import yfinance as yf
import pandas as pd
import requests

def get_gold_data():
    try:
        # یاہو فنانس سے کنکشن بنانے کے لیے ایک کسٹم ہیڈر سیشن تیار کرنا
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        # یاہو فنانس پر لائیو گولڈ کا ٹکر GC=F ہے
        ticker = yf.Ticker("GC=F", session=session)
        
        # 1 دن کا ڈیٹا 5 منٹ کی کینڈلز کے ساتھ ڈاؤن لوڈ کرنا
        df = ticker.history(period="1d", interval="5m", timeout=15)
        
        if df.empty:
            raise Exception("Yahoo Finance returned an empty dataframe on this cloud IP.")
            
        # کالمز کے نام چھوٹے حروف میں تبدیل کرنا تاکہ اسٹریٹیجی فائل چل سکے
        df = df.reset_index()
        df = df.rename(columns={
            "Datetime": "datetime", 
            "Open": "open", 
            "High": "high", 
            "Low": "low", 
            "Close": "close", 
            "Volume": "volume"
        })
        
        # ڈیٹا ٹائپ درست کرنا
        for col in ["open", "high", "low", "close"]:
            df[col] = df[col].astype(float)
            
        return df
        
    except Exception as e:
        raise Exception(f"Yahoo Cloud Bypass Error: {e}")
