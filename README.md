Stock Visualizer with RL Trading
An interactive web application to visualize stock prices and train reinforcement learning (RL) models for algorithmic trading using Dash, Plotly, and Stable-Baselines3.
Features

Visualize stock prices (NVDA, AAPL, MSFT, GOOGL, AMZN) with bar or line charts.
Adjust time range (1 to 12 months) with a slider.
Toggle 20-day and 50-day moving averages.
Real-time updates every minute for intraday data (≤ 1 month).
Train and visualize RL-based trading strategies using PPO.
Export data as CSV.
Dark/light mode toggle and responsive design.

Project Structure
stock_visualizer/
├── app.py                  # Main Dash application
├── data/
│   └── fetcher.py          # Fetch stock data
├── components/
│   ├── plots.py            # Plotly charts
│   └── rl_visualizer.py    # RL trading visualization
├── rl/
│   ├── environment.py      # Custom trading environment
│   ├── models.py           # RL algorithms (PPO)
│   └── trainer.py          # Training and evaluation
├── utils/
│   └── helpers.py          # Utility functions (CSV export)
├── config/
│   └── settings.py         # Configuration
├── static/
│   └── styles.css          # Custom CSS
├── tests/
│   └── test_rl.py          # Unit tests
├── requirements.txt        # Dependencies
└── README.md               # Documentation

Prerequisites

Python 3.8 or higher
pip

Installation

Clone or download the repository.
Navigate to the project directory:cd stock_visualizer


Create a virtual environment (optional):python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install dependencies:pip install -r requirements.txt



Running the Application

Run the Dash app:python app.py


Open http://127.0.0.1:8050 in a web browser.

Usage

Stock Visualization: Select stocks, adjust time range, toggle chart type and moving averages.
RL Trading: Choose a ticker, click "Train Model" to train a PPO model, and view trading performance (buy/sell markers, net worth).
Data Export: Download OHLCV and moving average data as CSV.
Real-Time Updates: Intraday data updates every minute for ≤ 1 month ranges.

Troubleshooting

yfinance Errors: Update yfinance (pip install --upgrade yfinance). Test with:from data.fetcher import fetch_historical_data
from datetime import datetime, timedelta
data = fetch_historical_data("NVDA", datetime.now() - timedelta(days=30), datetime.now(), context="test")
print(data)


Dash Issues: Ensure port 8050 is free. Try a different port:app.run(debug=True, port=8051)


RL Errors: Verify gymnasium and stable-baselines3 installations. Run tests:python -m unittest tests/test_rl.py



Contributing
Submit issues or pull requests to enhance the application.
License
MIT License
