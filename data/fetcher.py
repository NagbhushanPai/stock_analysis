import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD
from datetime import datetime, timedelta
import cachetools

# Cache to avoid repeated downloads
@cachetools.cached(cache=cachetools.LRUCache(maxsize=10))
def fetch_historical_data(ticker, start_date, end_date, interval="1d", context=None):
    """
    Fetch historical stock data with technical indicators.
    
    Args:
        ticker (str): Stock ticker.
        start_date (datetime): Start date.
        end_date (datetime): End date.
        interval (str): Data interval (e.g., "1d").
        context (str): Context for caching (e.g., "rl", "chart").
    
    Returns:
        pd.DataFrame: Data with price and indicators.
    """
    try:
        # Fetch data from yfinance
        stock = yf.Ticker(ticker)
        data = stock.history(start=start_date, end=end_date, interval=interval)
        if data.empty:
            raise ValueError(f"No data available for {ticker}")
        
        # Compute moving averages
        data['MA20'] = data['Close'].rolling(window=20).mean()
        data['MA50'] = data['Close'].rolling(window=50).mean()
        
        # Compute RSI
        rsi = RSIIndicator(data['Close'], window=14)
        data['RSI'] = rsi.rsi()
        
        # Compute MACD
        macd = MACD(data['Close'], window_slow=26, window_fast=12, window_sign=9)
        data['MACD'] = macd.macd()
        data['MACD_Signal'] = macd.macd_signal()
        
        # Handle NaN values
        data = data.dropna()
        
        # Add context-specific handling if needed
        if context == "rl":
            pass  # Already normalized in environment.py
        elif context == "chart":
            pass  # Used as-is for plotting
        
        return data
    
    except Exception as e:
        print(f"Error fetching data for {ticker}: {str(e)}")
        return pd.DataFrame()

# Example usage (for testing)
if __name__ == "__main__":
    end_date = datetime.now()
    start_date = end_date - timedelta(days=360)
    data = fetch_historical_data("NVDA", start_date, end_date, context="chart")
    print(data.head())