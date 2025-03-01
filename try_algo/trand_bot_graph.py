import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

# Trading strategy parameters
SMA_PERIOD = 10
EMA_PERIOD = 10
STOP_LOSS = 0.99  # 1% stop-loss
TAKE_PROFIT = 1.52  # 2% take-profit
initial_balance = 10000  # INR
position = 0
cash = initial_balance
trade_log = []  # To track trades & PnL
trade_positions = []  # To track buy/sell points on graph
current_trade = None  # Active trade (if any)

# Initialize price & trade data
prices = []
sma_values = []
ema_values = []

# Function to calculate EMA
def calculate_ema(prices, period):
    if len(prices) < period:
        return None
    alpha = 2 / (period + 1)
    ema = prices[0]  # First price as initial EMA
    for price in prices[1:]:
        ema = (price * alpha) + (ema * (1 - alpha))
    return ema

# Trading logic: Checks for crossover signals & stop-loss/take-profit
def check_trade_signal():
    global position, cash, current_trade

    if len(sma_values) < 2 or len(ema_values) < 2:
        return None  # Not enough data

    prev_ema, curr_ema = ema_values[-2], ema_values[-1]
    prev_sma, curr_sma = sma_values[-2], sma_values[-1]

    if prev_ema is None or prev_sma is None:
        return None

    price = prices[-1]

    # Handle active trade (Stop-Loss / Take-Profit)
    if current_trade:
        buy_price = current_trade["price"]
        if price <= buy_price * STOP_LOSS:
            return "STOP_LOSS"
        if price >= buy_price * TAKE_PROFIT:
            return "TAKE_PROFIT"

    # BUY signal: EMA crosses above SMA
    if prev_ema < prev_sma and curr_ema > curr_sma and not current_trade:
        return "BUY"

    # SELL signal: EMA crosses below SMA
    if prev_ema > prev_sma and curr_ema < curr_sma and current_trade:
        return "SELL"

    return None

# Function to update the graph dynamically
def update(frame):
    global prices, sma_values, ema_values, position, cash, current_trade

    # Simulate live market price
    new_price = prices[-1] + random.uniform(-1, 1) if prices else 100  # Start at 100
    prices.append(new_price)

    # Compute SMA
    if len(prices) >= SMA_PERIOD:
        sma_values.append(np.mean(prices[-SMA_PERIOD:]))
    else:
        sma_values.append(None)

    # Compute EMA
    ema_values.append(calculate_ema(prices, EMA_PERIOD))

    # Check for buy/sell signals
    signal = check_trade_signal()

    # Execute trades
    if signal == "BUY":
        cash -= new_price
        position += 1
        current_trade = {"price": new_price}
        trade_positions.append(("BUY", len(prices) - 1, new_price))
        print(f"🔼 BUY at {new_price:.2f}, Cash left: {cash:.2f}")

    elif signal in ["SELL", "STOP_LOSS", "TAKE_PROFIT"]:
        if position > 0:
            sell_price = new_price
            buy_price = current_trade["price"]
            profit = sell_price - buy_price
            trade_log.append(profit)
            cash += sell_price
            position -= 1
            trade_positions.append(("SELL", len(prices) - 1, sell_price))
            print(f"🔽 SELL at {sell_price:.2f}, Profit: {profit:.2f}, Cash: {cash:.2f}")
            current_trade = None  # Reset trade

    # Clear the plot and redraw
    ax.clear()
    ax.plot(prices, label="Price", color='blue', linewidth=1.5)
    if len(prices) >= SMA_PERIOD:
        ax.plot(sma_values, label=f"SMA ({SMA_PERIOD})", color='orange', linestyle="dashed")
    if len(prices) >= EMA_PERIOD:
        ax.plot(ema_values, label=f"EMA ({EMA_PERIOD})", color='red')

    # Mark buy/sell signals
    for trade_type, idx, trade_price in trade_positions:
        color = 'green' if trade_type == "BUY" else 'red'
        ax.scatter(idx, trade_price, color=color, marker="o", s=100, label=trade_type)

    ax.set_title("Live Market Prices with SMA & EMA (Trading Bot)")
    ax.set_ylabel("Price")
    ax.set_xlabel("Time (Ticks)")

# Set up Matplotlib figure
fig, ax = plt.subplots()

# Animate the graph
ani = animation.FuncAnimation(fig, update, interval=500)
plt.show()
