from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas_ta as ta

app = Flask(__name__)

def generate_signal(symbol, timeframe):
    # Data fetch from yfinance (Real-time)
    df = yf.download(symbol, period='1d', interval=f'{timeframe}m')
    
    # Technical Analysis using pandas_ta
    df['EMA_9'] = ta.ema(df['Close'], length=9)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    # Logic: Breakout & Price Action
    last_close = df['Close'].iloc[-1]
    last_ema = df['EMA_9'].iloc[-1]
    last_rsi = df['RSI'].iloc[-1]
    
    # Signal Generation Rules
    if last_close > last_ema and last_rsi < 70:
        return "CALL (Strong Buy)", "🟢"
    elif last_close < last_ema and last_rsi > 30:
        return "PUT (Strong Sell)", "🔴"
    else:
        return "AVOID TRADE", "🟡"

@app.route('/get_signal/<asset>/<timeframe>')
def get_signal(asset, timeframe):
    # Symbol format adjust for yfinance
    symbol = asset.replace("/", "") + "=X"
    signal, icon = generate_signal(symbol, timeframe)
    return jsonify({"signal": signal, "icon": icon})

if __name__ == '__main__':
    app.run()
