Stock Visualizer
An interactive web application to visualize stock prices using Dash and Plotly. Features include a time slider to adjust the date range (1 to 12 months) and checkboxes to select stocks (NVDA, AAPL, MSFT, GOOGL, AMZN).
Project Structure
stock_visualizer/
├── app.py                  # Main Dash application
├── data/
│   └── fetcher.py          # Functions for fetching stock data
├── components/
│   └── plots.py            # Functions for generating Plotly charts
├── config/
│   └── settings.py         # Configuration (tickers, colors, etc.)
├── requirements.txt        # List of dependencies
└── README.md               # Project documentation

Prerequisites

Python 3.8 or higher
pip (Python package manager)

Installation

Clone or download the repository.
Navigate to the project directory:cd stock_visualizer


Create a virtual environment (optional but recommended):python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install dependencies:pip install -r requirements.txt



Running the Application

Ensure you're in the stock_visualizer directory.
Run the Dash app:python app.py


Open a web browser and go to http://127.0.0.1:8050 (or the URL shown in the terminal).

Usage

Select Stocks: Use the checkboxes to choose which stocks to display.
Adjust Time Range: Move the slider to set the time range (1 to 12 months).
Interact with the Chart: Hover over bars for details, zoom/pan, or download the chart as a PNG.

Troubleshooting

yfinance Errors: If data fetching fails, ensure yfinance is updated (pip install --upgrade yfinance). Check your internet connection or try alternative APIs (e.g., Polygon.io).
Dash Issues: Ensure port 8050 is free. If the server fails, try a different port by modifying app.run(debug=True, port=8051) in app.py.
Dependencies: Verify all packages are installed (pip install -r requirements.txt).

Contributing
Feel free to submit issues or pull requests to enhance the application.
License
MIT License
