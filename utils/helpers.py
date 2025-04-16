import pandas as pd
from datetime import datetime, timedelta
from data.fetcher import fetch_historical_data
from config.settings import TICKERS

def generate_csv_download(selected_stocks, months):
    """
    Generate a CSV file with stock data for download.
    
    Args:
        selected_stocks (list): List of stock tickers.
        months (int): Number of months for the time range.
    
    Returns:
        dict: Dash download data.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)
    interval = "1m" if months <= 1 else "1d"
    
    all_data = []
    for ticker in selected_stocks:
        if ticker in TICKERS:
            data = fetch_historical_data(ticker, start_date, end_date, interval=interval)
            if not data.empty:
                data = data.reset_index()
                data['Ticker'] = ticker
                all_data.append(data[['Ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'MA20', 'MA50']])
    
    if all_data:
        df = pd.concat(all_data, ignore_index=True)
        return dict(content=df.to_csv(index=False), filename=f"stock_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    return None