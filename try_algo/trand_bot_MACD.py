import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Load CSV file
df = pd.read_csv("try_algo\chart.csv")

# Convert DateTime column to datetime format
df['DateTime'] = pd.to_datetime(df['DateTime'])
df.set_index('DateTime', inplace=True)

# Fill missing values (optional: forward fill)
df.ffill(inplace=True)

# Extract price column
prices = df['WIPROEQN'].dropna().values.tolist()

# Trading strategy parameters
SHORT_EMA = 12
LONG_EMA = 26
SIGNAL_PERIOD = 9
SMA_PERIOD = 10
EMA_PERIOD = 10
STOP_LOSS = 0.99  # 1% stop-loss
TAKE_PROFIT = 1.02  # 2% take-profit
initial_balance = 10000  # INR
position = 0
cash = initial_balance
trade_log = {"MACD": [], "SMA": [], "EMA": []}  # Track profits separately
trade_positions = []  # To track buy/sell points on graph
current_trade = None  # Active trade (if any)

# Initialize indicator calculations
macd_values = []
signal_values = []
sma_values = []
ema_values = []

# Function to update MACD
def update_macd():
    if len(prices) < LONG_EMA:
        return None, None
    short_ema = pd.Series(prices).ewm(span=SHORT_EMA, adjust=False).mean()
    long_ema = pd.Series(prices).ewm(span=LONG_EMA, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=SIGNAL_PERIOD, adjust=False).mean()
    return macd.iloc[-1], signal.iloc[-1]

# Function to update SMA & EMA
def update_sma_ema():
    if len(prices) < SMA_PERIOD:
        return None, None
    sma = pd.Series(prices).rolling(SMA_PERIOD).mean().iloc[-1]
    ema = pd.Series(prices).ewm(span=EMA_PERIOD, adjust=False).mean().iloc[-1]
    return sma, ema

# Trading logic: Checks for buy/sell signals & stop-loss/take-profit
def check_trade_signal(strategy):
    global position, cash, current_trade
    price = prices[-1]
    
    if strategy == "MACD":
        if len(macd_values) < 2 or len(signal_values) < 2:
            return None
        prev_macd, curr_macd = macd_values[-2], macd_values[-1]
        prev_signal, curr_signal = signal_values[-2], signal_values[-1]
        
        if prev_macd is None or curr_macd is None or prev_signal is None or curr_signal is None:
            return None
        
        if prev_macd < prev_signal and curr_macd > curr_signal and not current_trade:
            return "BUY"
        if prev_macd > prev_signal and curr_macd < curr_signal and current_trade:
            return "SELL"
    
    elif strategy == "SMA/EMA":
        if len(sma_values) < 2 or len(ema_values) < 2:
            return None
        prev_ema, curr_ema = ema_values[-2], ema_values[-1]
        prev_sma, curr_sma = sma_values[-2], sma_values[-1]
        
        if prev_ema is None or curr_ema is None or prev_sma is None or curr_sma is None:
            return None
        
        if prev_ema < prev_sma and curr_ema > curr_sma and not current_trade:
            return "BUY"
        if prev_ema > prev_sma and curr_ema < curr_sma and current_trade:
            return "SELL"
    
    return None

# Function to update the graph dynamically
def update(frame):
    global prices, macd_values, signal_values, sma_values, ema_values, position, cash, current_trade
    if frame >= len(df):
        return
    
    new_price = df['WIPROEQN'].iloc[frame]
    prices.append(new_price)
    macd, signal = update_macd()
    sma, ema = update_sma_ema()
    
    macd_values.append(macd)
    signal_values.append(signal)
    sma_values.append(sma)
    ema_values.append(ema)
    
    for strategy in ["MACD", "SMA/EMA"]:
        signal_type = check_trade_signal(strategy)
        if signal_type == "BUY":
            cash -= new_price
            position += 1
            current_trade = {"price": new_price, "strategy": strategy}
            trade_positions.append((strategy, "BUY", frame, new_price))
            print(f"🔼 {strategy} BUY at {new_price:.2f}, Cash left: {cash:.2f}")
        elif signal_type == "SELL" and current_trade:
            sell_price = new_price
            buy_price = current_trade["price"]
            profit = sell_price - buy_price
            trade_log[current_trade["strategy"].append(profit)]
            cash += sell_price
            position -= 1
            trade_positions.append((current_trade["strategy"], "SELL", frame, sell_price))
            print(f"🔽 {current_trade['strategy']} SELL at {sell_price:.2f}, Profit: {profit:.2f}, Cash: {cash:.2f}")
            current_trade = None
    
    ax1.clear()
    ax1.plot(prices, label="Price", color='blue', linewidth=1.5)
    if len(macd_values) > 1:
        ax2.clear()
        ax2.plot(macd_values, label="MACD", color='purple')
        ax2.plot(signal_values, label="Signal", color='red', linestyle="dashed")
    if len(sma_values) > 1:
        ax1.plot(sma_values, label=f"SMA ({SMA_PERIOD})", color='orange', linestyle="dashed")
        ax1.plot(ema_values, label=f"EMA ({EMA_PERIOD})", color='red')
    
    ax1.legend()
    ax2.legend()

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
ani = animation.FuncAnimation(fig, update, frames=len(df), interval=500)
plt.show()