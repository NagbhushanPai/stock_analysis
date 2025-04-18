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
*   **Reinforcement Learning Trading**:
    *   Train RL agents (PPO or SAC algorithms) on historical stock data.
    *   Visualize the agent's trading performance (buy/sell actions, net worth over time).
    *   Real-time training progress bar and Estimated Time Remaining (ETA) displayed in the web UI.
    *   Visual training progress bar and ETA also shown in the **terminal using `tqdm`**.
    *   Calculates and displays performance metrics (Sharpe Ratio, Max Drawdown, Total Reward).

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

## Prerequisites

*   Python 3.8 or higher
*   pip (Python package installer)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd stock_analysis
    ```
2.  **Create and activate a virtual environment (recommended):**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

1.  **Run the Dash app:**
    ```bash
    python app.py
    ```
2.  **Open your web browser** and navigate to `http://127.0.0.1:8050` (or the address shown in the terminal).

## Usage

1.  **Stock Visualization**:
    *   Use the "Select Stock" dropdown to choose a ticker.
    *   Adjust the "Time Range (Months)" slider.
    *   Select indicators like "RSI" or "MACD" using the checklist. The chart will update automatically.
2.  **RL Model Training**:
    *   Select the desired stock ticker under "Train RL Model".
    *   Choose the RL algorithm ("PPO" or "SAC") from the dropdown.
    *   Click the "Train Model" button.
    *   Observe the progress bar and ETA in the UI below the buttons. Progress is also printed in the terminal where `app.py` is running.
    *   Once training is complete, the "RL Chart" will display the agent's actions and net worth, and metrics will appear below it. Trained models are saved in the `models/` directory.
3.  **RSI Strategy Backtesting**:
    *   Select the stock ticker and time range as desired.
    *   Click the "Backtest RSI Strategy" button.
    *   The "RL Chart" will display the strategy's actions and net worth, along with performance metrics.

## Troubleshooting

*   **`yfinance` Errors**: If you encounter issues fetching data, try updating `yfinance`:
    ```bash
    pip install --upgrade yfinance
    ```
    You can test fetching directly:
    ```python
    # test_fetch.py
    from data.fetcher import fetch_historical_data
    from datetime import datetime, timedelta
    try:
        data = fetch_historical_data("NVDA", datetime.now() - timedelta(days=30), datetime.now(), context="test")
        print(data.head())
        print("Fetch successful!")
    except Exception as e:
        print(f"Fetch failed: {e}")

    # Run with: python test_fetch.py
    ```
*   **Dash Server Issues**: Ensure port 8050 is not already in use. If it is, you can specify a different port when running the app:
    ```bash
    python app.py --port 8051
    ```
    *(Note: Command-line argument parsing for port needs to be added to `app.py` if not already present. Alternatively, modify `app.run(debug=True, port=8051)` directly in `app.py`)*.
*   **RL Errors**: Ensure `stable-baselines3`, `gymnasium`, and `tensorflow` or `torch` (depending on SB3 backend) are correctly installed. Check `requirements.txt`.

## Contributing

Contributions, issues, and feature requests are welcome. Please feel free to submit issues or pull requests to enhance the application.

## License

This project is licensed under the MIT License. See the LICENSE file for details (if one exists).
