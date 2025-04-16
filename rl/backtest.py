import pandas as pd
import numpy as np
from data.fetcher import fetch_historical_data
from datetime import datetime, timedelta
from ta.momentum import RSIIndicator

def rsi_strategy(data):
    """
    RSI-based trading strategy.
    
    Args:
        data (pd.DataFrame): Stock data up to current step.
    
    Returns:
        int: 1 (buy), 2 (sell), 0 (hold).
    """
    rsi = RSIIndicator(data['Close']).rsi().iloc[-1]
    if rsi < 30:
        return 1  # Buy
    elif rsi > 70:
        return 2  # Sell
    return 0  # Hold

def backtest_strategy(ticker, months, strategy_func):
    """
    Backtest a trading strategy.
    
    Args:
        ticker (str): Stock ticker.
        months (int): Data range in months.
        strategy_func: Function mapping data to actions (buy, sell, hold).
    
    Returns:
        dict: Performance metrics.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)
    data = fetch_historical_data(ticker, start_date, end_date, interval="1d", context="backtest")
    if data.empty:
        return {"error": f"No data for {ticker}"}
    
    balance = 10000
    shares_held = 0
    net_worths = []
    
    for i in range(len(data)):
        action = strategy_func(data.iloc[:i+1])
        price = data['Close'].iloc[i]
        if action == 1:  # Buy
            shares_to_buy = balance // price
            balance -= shares_to_buy * price
            shares_held += shares_to_buy
        elif action == 2:  # Sell
            balance += shares_held * price
            shares_held = 0
        net_worths.append(balance + shares_held * price)
    
    returns = pd.Series(net_worths).pct_change().dropna()
    sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
    max_drawdown = (max(net_worths) - min(net_worths)) / max(net_worths) if max(net_worths) > 0 else 0
    
    return {
        'final_net_worth': net_worths[-1],
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'net_worths': net_worths
    }