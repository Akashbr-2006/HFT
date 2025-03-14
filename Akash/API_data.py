from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
import asyncio
import random

app = FastAPI()

# Order book structure
order_book = {"bids": [], "asks": []}

class Order(BaseModel):
    side: str  # "buy" or "sell"
    price: float
    size: int

@app.get("/order_book")
def get_order_book():
    """Returns the current order book."""
    return order_book

@app.post("/place_order")
def place_order(order: Order):
    """Handles order placement."""
    if order.side == "buy":
        order_book["bids"].append((order.price, order.size))
        order_book["bids"].sort(reverse=True)  # Highest bid first
    else:
        order_book["asks"].append((order.price, order.size))
        order_book["asks"].sort()  # Lowest ask first
    return {"status": "order placed", "order": order}

@app.websocket("/market_data")
async def market_data_feed(websocket: WebSocket):
    """WebSocket stream for real-time market data."""
    await websocket.accept()
    while True:
        # Simulate order book updates
        best_bid = max(order_book["bids"], default=(0, 0))
        best_ask = min(order_book["asks"], default=(float('inf'), 0))
        spread = best_ask[0] - best_bid[0] if best_ask[0] > best_bid[0] else 0
        market_data = {
            "best_bid": best_bid,
            "best_ask": best_ask,
            "spread": spread,
            "bids": order_book["bids"],
            "asks": order_book["asks"]
        }
        await websocket.send_json(market_data)
        await asyncio.sleep(1)  # Simulate live market updates
