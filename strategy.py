def check_signal(data):
    if data is None or len(data) < 30:
        return None

    df = calculate_indicators(data)
    
    # لائیو کینڈل چیک کریں
    last = df.iloc[-1]
    
    # لائیو قیمت حاصل کرنا
    entry = round(last["close"], 2)
    rsi_val = round(last['rsi'], 2)
    
    # آر ایس آئی کے پکے اور محفوظ اوور باٹ اور اوور سولڈ سگنلز (کلاؤڈ محفوظ طریقہ)
    # اگر گولڈ کی قیمت بہت گر جائے (RSI 30 سے نیچے ہو) تو بائی کا سگنل بنے گا
    is_buy = rsi_val <= 30
    # اگر گولڈ کی قیمت بہت بڑھ جائے (RSI 70 سے اوپر ہو) تو سیل کا سگنل بنے گا
    is_sell = rsi_val >= 70
    
    if is_buy:
        sl = round(entry - 5.00, 2)  # $5.00 کا سٹاپ لاس
        tp = round(entry + 10.00, 2) # $10.00 کا ٹیک پرافٹ
        return {"signal": "BUY 📈", "entry": entry, "sl": sl, "tp": tp, "rsi": rsi_val}
        
    elif is_sell:
        sl = round(entry + 5.00, 2)
        tp = round(entry - 10.00, 2)
        return {"signal": "SELL 📉", "entry": entry, "sl": sl, "tp": tp, "rsi": rsi_val}
        
    return None
