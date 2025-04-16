import plotly.graph_objects as go
from datetime import datetime, timedelta
from data.fetcher import fetch_historical_data
from config.settings import TICKERS, COLORS

def create_stock_bar_chart(selected_stocks, months):
    """
    Create a Plotly bar chart for selected stocks over a given time range.
    
    Args:
        selected_stocks (list): List of stock tickers to display.
        months (int): Number of months for the time range.
    
    Returns:
        go.Figure: Plotly figure object.
    """
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)
    
    # Initialize figure
    fig = go.Figure()
    
    # Fetch and plot data for each selected stock
    for i, ticker in enumerate(selected_stocks):
        if ticker in TICKERS:
            data = fetch_historical_data(ticker, start_date, end_date)
            if not data.empty:
                fig.add_trace(go.Bar(
                    x=data.index,
                    y=data['Close'],
                    name=ticker,
                    marker_color=COLORS[i % len(COLORS)],
                    opacity=0.8
                ))
    
    # Update layout
    fig.update_layout(
        title=f'Stock Prices (Last {months} Months)',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        barmode='group',
        xaxis_tickangle=-45,
        showlegend=True,
        height=600,
        margin=dict(b=200)  # Extra space for rotated x-axis labels
    )
    
    return fig