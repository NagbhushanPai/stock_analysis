Stock Visualizer
An interactive web application to visualize stock prices using Dash and Plotly. Features include:

Time slider to adjust the date range (1 to 12 months).
Checkboxes to select stocks (NVDA, AAPL, MSFT, GOOGL, AMZN).
Toggle between bar and line charts.
Optional 20-day and 50-day moving averages.
Real-time updates every minute for intraday data (when time range ≤ 1 month).
Data export as CSV.
Dark/light mode toggle and responsive design.

Project Structure
stock_visualizer/
├── app.py                  # Main Dash application
├── data/
│   └── fetcher.py          # Functions for fetching stock data
├── components/
│   └── plots.py            # Functions for generating Plotly charts
├── config/
│   └── settings.py         # Configuration (tickers, colors, etc.)
├── utils/
│   └── helpers.py          # Utility functions (e.g., CSV export)
├── static/
│   └── styles.css          # Custom CSS for styling
├── requirements.txt        # List of dependencies
└── README.md               # Project documentation

Prerequisites

Python 3.8 or higher
pip (Python package manager)

Installation

Clone or download the repository.

Navigate to the project directory:
cd stock_visualizer


Create a virtual environment (optional but recommended):
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install dependencies:
pip install -r requirements.txt



Running the Application

Ensure you're in the stock_visualizer directory.

Run the Dash app:
python app.py


Open a web browser and go to http://127.0.0.1:8050.


Usage

Select Stocks: Use checkboxes to choose stocks to display.
Adjust Time Range: Move the slider to set the time range (1 to 12 months).
Chart Type: Toggle between bar and line charts.
Moving Averages: Enable 20-day and/or 50-day moving averages.
Download Data: Click the "Download Data as CSV" button to export data.
Dark Mode: Toggle between light and dark themes.
Real-Time Updates: For time ranges ≤ 1 month, the chart updates every minute with intraday data.

Troubleshooting

yfinance Errors: If data fetching fails, update yfinance (pip install --upgrade yfinance). Check your internet connection or try alternative APIs (e.g., Polygon.io).
Dash Issues: Ensure port 8050 is free. If the server fails, try a different port by modifying app.run(debug=True, port=8051) in app.py.
Dependencies: Verify all packages are installed (pip install -r requirements.txt).
CSS Issues: Ensure the static folder is in the project root and accessible.

Contributing
Submit issues or pull requests to enhance the application.
License
MIT License
