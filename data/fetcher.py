import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
from cachetools import TTLCache

# Cache with 5-minute TTL (300 seconds)
cache = TTLCache(maxsize=100, ttl=300)

def fetch_historical_data(ticker, start_date, end_date, interval="1d", retries=3, delay=5, context="chart"):
    """
    Fetch historical stock data for a given ticker from Yahoo Finance.
    
    Args:
        ticker (str): Stock ticker symbol (e.g., 'NVDA').
        start_date (datetime): Start date for data.
        end_date (datetime): End date for data.
        interval (str): Data interval ('1d' for daily, '1m' for 1-minute).
        retries (int): Number of retry attempts for failed requests.
        delay (int): Delay between retries in seconds.
        context (str): Context of the fetch (e.g., 'chart', 'csv').
    
    Returns:
        pd.DataFrame: Historical stock data or empty DataFrame if failed.
    """
    # Create cache key
    cache_key = f"{ticker}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}_{interval}"
    
    # Check cache
    if cache_key in cache:
        print(f"Using cached data for {ticker} ({context})")
        return cache[cache_key]
    
    print(f"Fetching {ticker} historical data (interval: {interval}, context: {context})...")
    for attempt in range(retries):
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(start=start_date, end=end_date, interval=interval)
            if not data.empty:
                print(f"Downloaded {len(data)} records of {ticker} data ({context})")
                # Calculate moving averages
                data['MA20'] = data['Close'].rolling(window=20).mean()
                data['MA50'] = data['Close'].rolling(window=50).mean()
                # Store in cache
                cache[cache_key] = data
                return data
            else:
                print(f"No data returned for {ticker}, attempt {attempt + 1}/{retries} ({context})")
        except Exception as e:
            print(f"Error fetching {ticker} (attempt {attempt + 1}/{retries}, context: {context}): {e}")
        if attempt < retries - 1:
            time.sleep(delay)
    print(f"Failed to fetch data for {ticker} after {retries} attempts ({context})")
    return pd.DataFrame()