from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas as pd
import pandas_ta as ta

app = Flask(__name__)

# Yahan apni API Key daalein agar aap koi paid service use kar rahe hain
# Agar yfinance use kar rahe hain, toh iski zarurat nahi hai.
API_KEY = "N8I9XB3N21L0RJ40" 

def generate_signal(symbol, timeframe):
    try:
        # Yahoo Finance se data le rahe hain (No API Key required for yfinance)
        ticker = yf.Ticker(symbol)
        df = ticker.history(period='1d', interval=f'{timeframe}m')
        
        if df.empty:
            return "NO DATA", "⚪"

        # Indicators Calculation
        df['EMA_9'] = ta.ema(df['Close'], length=9)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        last_close = df['Close'].iloc[-1]
        last_ema = df['EMA_9'].iloc[-1]
        last_rsi = df['RSI'].iloc[-1]
        
        # Logic
        if last_close > last_ema and last_rsi < 70:
            return "CALL (Strong Buy)", "🟢"
        elif last_close < last_ema and last_rsi > 30:
            return "PUT (Strong Sell)", "🔴"
        else:
            return "WAIT/NO TRADE", "🟡"
    except Exception as e:
        return "SERVER ERROR", "⚪"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_signal/<asset>/<timeframe>')
def get_signal(asset, timeframe):
    # Yahoo Finance symbol format (e.g., EURUSD=X)
    symbol = asset.replace("/", "") + "=X"
    signal, icon = generate_signal(symbol, timeframe)
    return jsonify({"signal": signal, "icon": icon})

if __name__ == '__main__':
    app.run(debug=True)
    
