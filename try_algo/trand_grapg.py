import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

# Set moving average period
SMA_PERIOD = 10
EMA_PERIOD = 10

# Initialize price data
prices = []
sma_values = []
ema_values = []

# Exponential moving average calculation (initial value = first price)
def calculate_ema(prices, period):
    if len(prices) < period:
        return None  # Not enough data
    alpha = 2 / (period + 1)  # EMA smoothing factor
    ema = prices[0]  # First price as initial EMA
    for price in prices[1:]:
        ema = (price * alpha) + (ema * (1 - alpha))
    return ema

# Function to update the plot dynamically
def update(frame):
    global prices, sma_values, ema_values

    # Simulate new price (random movement)
    new_price = prices[-1] + random.uniform(-1, 1) if prices else 100  # Start at 100
    prices.append(new_price)

    # Compute SMA
    if len(prices) >= SMA_PERIOD:
        sma_values.append(np.mean(prices[-SMA_PERIOD:]))  # Take last N prices and average
    else:
        sma_values.append(None)  # Not enough data

    # Compute EMA
    ema_values.append(calculate_ema(prices, EMA_PERIOD))

    # Clear the plot
    ax.clear()

    # Plot live prices
    ax.plot(prices, label="Price", color='blue', linewidth=1.5)
    
    # Plot SMA
    if len(prices) >= SMA_PERIOD:
        ax.plot(sma_values, label=f"SMA ({SMA_PERIOD})", color='orange', linestyle="dashed")

    # Plot EMA
    if len(prices) >= EMA_PERIOD:
        ax.plot(ema_values, label=f"EMA ({EMA_PERIOD})", color='red')

    # Add labels and legend
    ax.set_title("Live Market Prices with SMA & EMA")
    ax.set_ylabel("Price")
    ax.set_xlabel("Time (Ticks)")
    ax.legend()

# Set up Matplotlib figure
fig, ax = plt.subplots()

# Animate the graph
ani = animation.FuncAnimation(fig, update, interval=500)  # Update every 500ms
plt.show()
