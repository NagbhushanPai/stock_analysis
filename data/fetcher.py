import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

def fetch_historical_data(ticker, start_date, end_date, retries=3, delay=5):
    """
    Fetch historical stock data for a given ticker from Yahoo Finance.
    
    Args:
        ticker (str): Stock ticker symbol (e.g., 'NVDA').
        start_date (datetime): Start date for data.
        end_date (datetime): End date for data.
        retries (int): Number of retry attempts for failed requests.
        delay (int): Delay between retries in seconds.
    
    Returns:
        pd.DataFrame: Historical stock data or empty DataFrame if failed.
    """
    print(f"Fetching {ticker} historical data...")
    for attempt in range(retries):
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(start=start_date, end=end_date, interval="1d")
            if not data.empty:
                print(f"Downloaded {len(data)} days of {ticker} data")
                return data
            else:
                print(f"No data returned for {ticker}, attempt {attempt + 1}/{retries}")
        except Exception as e:
            print(f"Error fetching {ticker} (attempt {attempt + 1}/{retries}): {e}")
        if attempt < retries - 1:
            time.sleep(delay)
    print(f"Failed to fetch data for {ticker} after {retries} attempts")
    return pd.DataFrame()