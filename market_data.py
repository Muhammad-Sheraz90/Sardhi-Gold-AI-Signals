import requests

def get_gold_price():
    try:
        # Binance API سے PAXG/USDT (جو کہ گولڈ کی لائیو قیمت کے برابر ہوتا ہے) کا ریٹ لینا
        url = "https://binance.com"
        response = requests.get(url)
        data = response.json()
        
        if 'price' in data:
            price = float(data['price'])
            return price
        else:
            print("⚠️ API سے ڈیٹا نہیں مل سکا۔")
            return None
            
    except Exception as e:
        print(f"❌ Market Data Error: {e}")
        return None
