import asyncio
import requests
import random
import time

# API endpoint from your Flask mock market
API_URL = "http://127.0.0.1:5000/market_data"

# Simulated order book (tracks our placed orders)
open_orders = {"bid": None, "ask": None}
position = 0  # Inventory tracking (positive = long, negative = short)
average_buy_price = 0  # Tracks avg price for PnL calculations
realized_pnl = 0  # Tracks closed trade profits

# Configurable trading parameters
SPREAD = 0.05  # Initial spread for market making
STOP_LOSS_THRESHOLD = 1  # If price drops too much, exit positions
ORDER_MIN_LIFETIME = 5  # Orders should live for at least 5 seconds
CANCEL_THRESHOLD = 0.02  # Minimum price movement required to cancel orders

last_order_time = time.time()  # Tracks the last order placement time

async def fetch_market_data():
    """ Fetches live market data from the API """
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Market Data: {data}")  # Debugging
            return data
    except Exception as e:
        print(f"❌ Error fetching market data: {e}")
    return None

async def place_order(side, price, size, market_data):
    """ Simulates placing a buy/sell order """
    global open_orders, position, average_buy_price, realized_pnl, last_order_time
    print(f"📌 Placing {side.upper()} order: {size} units @ {price}")

    open_orders[side] = {"price": price, "size": size}
    last_order_time = time.time()  # Update order timestamp

    # Simulating trade execution if market moves to our order
    if side == "bid" and market_data["best_ask"] <= price:
        new_total_cost = (average_buy_price * position) + (price * size)
        position += size
        average_buy_price = new_total_cost / position if position > 0 else 0
        print(f"✅ Buy filled at {price}, new position: {position}, Avg Buy: {average_buy_price:.2f}")

    elif side == "ask" and market_data["best_bid"] >= price:
        position -= size
        profit = (price - average_buy_price) * size  # Calculate profit on this trade
        realized_pnl += profit
        print(f"✅ Sell filled at {price}, new position: {position}, Realized PnL: {realized_pnl:.2f}")

async def cancel_order(side):
    """ Cancels an existing order """
    global open_orders
    if open_orders[side]:
        print(f"❌ Canceling {side.upper()} order @ {open_orders[side]['price']}")
        open_orders[side] = None

async def calculate_pnl():
    """ Calculates and prints real-time PnL every second """
    global position, realized_pnl
    while True:
        market_data = await fetch_market_data()
        if market_data and position > 0:
            current_price = market_data["best_bid"]
            unrealized_pnl = (current_price - average_buy_price) * position
            total_pnl = realized_pnl + unrealized_pnl
            print(f"💰 Realized PnL: {realized_pnl:.2f}, Unrealized PnL: {unrealized_pnl:.2f}, Total PnL: {total_pnl:.2f}")
        await asyncio.sleep(1)  # Update every second

async def update_orders():
    """ Main logic for market-making strategy """
    global SPREAD, position, last_order_time

    while True:
        market_data = await fetch_market_data()
        if not market_data:
            await asyncio.sleep(0.1)
            continue

        mid_price = (market_data["best_bid"] + market_data["best_ask"]) / 2
        bid_price = round(mid_price - SPREAD / 2, 2)
        ask_price = round(mid_price + SPREAD / 2, 2)

        time_since_last_order = time.time() - last_order_time

        print(f"⏳ Time since last order: {time_since_last_order:.2f}s")  # Debugging

        # ⏳ Keep orders alive for at least ORDER_MIN_LIFETIME
        if time_since_last_order < ORDER_MIN_LIFETIME:
            await asyncio.sleep(0.5)
            continue

        # 🛑 Only cancel orders if price moved significantly
        if (
            open_orders["bid"] and abs(open_orders["bid"]["price"] - bid_price) < CANCEL_THRESHOLD and
            open_orders["ask"] and abs(open_orders["ask"]["price"] - ask_price) < CANCEL_THRESHOLD
        ):
            print(f"⏳ Keeping existing orders, no significant price movement.")
            await asyncio.sleep(0.5)
            continue

        # ❌ Cancel old orders if price has changed
        if open_orders["bid"] and open_orders["bid"]["price"] != bid_price:
            await cancel_order("bid")
        if open_orders["ask"] and open_orders["ask"]["price"] != ask_price:
            await cancel_order("ask")

        # 📌 Place new bid/ask orders
        print(f"📊 Attempting to place BID at {bid_price}, ASK at {ask_price}")  # Debugging
        await place_order("bid", bid_price, random.randint(1, 5), market_data)
        await place_order("ask", ask_price, random.randint(1, 5), market_data)

        # 🚨 Check for sudden price drops
        if position > 0 and market_data["best_bid"] < (mid_price - STOP_LOSS_THRESHOLD):
            print(f"⚠️ Market drop detected! Exiting position at {market_data['best_bid']}")
            await place_order("ask", market_data["best_bid"], position, market_data)  # Sell at market
            position = 0

        await asyncio.sleep(1)  # Run every 100ms

# Run both tasks (trading + PnL tracking)
async def main():
    await asyncio.gather(update_orders(), calculate_pnl())

asyncio.run(main())
