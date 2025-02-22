import requests
import pandas as pd
import time
from tabulate import tabulate


API_KEY = "VA7LH7H1A2CX3KKJ"
symbol = "IBM"


def fetch_stock_data():
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    time_series = data.get("Time Series (1min)", {})
    if not time_series:
        print("No data received. Check API key or rate limits.")
        return None

    # Convert to DataFrame
    df = pd.DataFrame.from_dict(time_series, orient="index")
    df = df.rename(columns={
        "1. open": "Open Price",
        "2. high": "High Price",
        "3. low": "Low Price",
        "4. close": "Close Price",
        "5. volume": "Volume"
    })
    
    # Reset index and rename columns
    df.reset_index(inplace=True)
    df.rename(columns={"index": "Time"}, inplace=True)
    
    return df

# **Live Streaming Loop**
while True:
    df = fetch_stock_data()
    if df is not None:
        print("\nLatest Stock Data for", symbol)
        print(tabulate(df.head(5), headers="keys", tablefmt="grid"))  
    time.sleep(60)  