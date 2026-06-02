from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas as pd

app = Flask(__name__)

def generate_signal(symbol, timeframe):
    try:
        # Fetching Market Data
        df = yf.download(symbol, period='5d', interval=f'{timeframe}m', progress=False)
        if df.empty: return "NO DATA", "⚪"

        # Indicators Calculation
        df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['RSI'] = 100 - (100 / (1 + df['Close'].diff().clip(lower=0).rolling(14).mean() / df['Close'].diff().clip(upper=0).abs().rolling(14).mean()))
        
        # Support/Resistance Logic (Pivot Points)
        pivot = df['High'].iloc[-2] + df['Low'].iloc[-2] + df['Close'].iloc[-2] / 3
        
        last_close = df['Close'].iloc[-1]
        last_ema = df['EMA_9'].iloc[-1]
        last_rsi = df['RSI'].iloc[-1]

        # Professional Trading Logic
        if last_close > pivot and last_close > last_ema and last_rsi < 65:
            return "STRONG CALL (BUY)", "🟢"
        elif last_close < pivot and last_close < last_ema and last_rsi > 35:
            return "STRONG PUT (SELL)", "🔴"
        else:
            return "WAIT / NO TRADE", "🟡"
    except:
        return "ERROR", "⚪"

@app.route('/')
def index(): return render_template('index.html')

@app.route('/get_signal/<asset>/<timeframe>')
def get_signal(asset, timeframe):
    symbol = asset.replace("/", "") + "=X"
    signal, icon = generate_signal(symbol, timeframe)
    return jsonify({"signal": signal, "icon": icon})

if __name__ == '__main__': app.run()
    
