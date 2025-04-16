# Stock tickers to display
TICKERS = ["NVDA", "AAPL", "MSFT", "GOOGL", "AMZN"]

# Colors for each stock
COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

# Chart types
CHART_TYPES = ['Bar', 'Line']

# Data intervals
INTERVALS = {
    'daily': '1d',
    'intraday': '1m'
}

# RL settings
RL_HYPERPARAMS = {
    'learning_rate': 0.0003,
    'n_steps': 2048,
    'batch_size': 64,
    'n_epochs': 10,
    'gamma': 0.99,
    'gae_lambda': 0.95
}