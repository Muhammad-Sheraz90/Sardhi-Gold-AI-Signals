import requests
import pandas as pd
from datetime import datetime

def get_gold_data():
    try:
        # کلاؤڈ محفوظ اور اوپن فنانشل ڈیٹا سٹریم (جو کلاؤڈ سرورز کو کبھی بلاک نہیں کرتا)
        url = "https://binance.com"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            # متبادل کلاؤڈ محفوظ سرور (اگر پہلی فیڈ میں کوئی تاخیر ہو)
            url = "https://cryptocompare.com"
            response = requests.get(url, timeout=15)
            res_data = response.json()
            data_list = res_data["Data"]["Data"]
            df = pd.DataFrame(data_list)
            df['datetime'] = pd.to_datetime(df['time'], unit='s')
            df = df.rename(columns={"open": "open", "high": "high", "low": "low", "close": "close", "volumeto": "volume"})
        else:
            # بین الاقوامی لائیو گولڈ فیڈ (PAXG) جو لائیو کینڈل فراہم کرتی ہے
            json_data = response.json()
            
            # کینڈل ڈیٹا کو پائتھون فریم میں ترتیب دینا
            df = pd.DataFrame(json_data, columns=[
                "timestamp", "open", "high", "low", "close", "volume", 
                "close_time", "asset_volume", "trades", "taker_buy_base", "taker_buy_quote", "ignore"
            ])
            
            # ٹائم فارمیٹ درست کرنا
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            
        # نان نمبرز یا خالی جگہ صاف کرنا
        df = df.dropna().reset_index(drop=True)
        
        # تمام مالیاتی کالمز کو فلوٹ (Float) میں تبدیل کرنا تاکہ اسٹریٹیجی حساب لگا سکے
        for col in ["open", "high", "low", "close"]:
            df[col] = df[col].astype(float)
            
        return df
        
    except Exception as e:
        raise Exception(f"Ultimate Cloud Feed Error: {e}")
