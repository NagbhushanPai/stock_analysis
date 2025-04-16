import plotly.graph_objects as go
from datetime import datetime, timedelta
from data.fetcher import fetch_historical_data
from config.settings import TICKERS, COLORS

def create_stock_chart(selected_stocks, months, chart_type, ma_options):
    """
    Create a Plotly chart for selected stocks over a given time range.
    
    Args:
        selected_stocks (list): List of stock tickers to display.
        months (int): Number of months for the time range.
        chart_type (str): 'Bar' or 'Line'.
        ma_options (list): List of moving averages to display ('20', '50').
    
    Returns:
        go.Figure: Plotly figure object.
    """
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)
    interval = "1m" if months <= 1 else "1d"
    
    # Initialize figure
    fig = go.Figure()
    
    # Fetch data once per stock
    for i, ticker in enumerate(selected_stocks):
        if ticker in TICKERS:
            data = fetch_historical_data(ticker, start_date, end_date, interval=interval, context="chart")
            if not data.empty:
                # Create chart trace
                trace = go.Bar if chart_type == 'Bar' else go.Scatter
                fig.add_trace(trace(
                    x=data.index,
                    y=data['Close'],
                    name=ticker,
                    marker_color=COLORS[i % len(COLORS)],
                    opacity=0.8,
                    hovertemplate=(
                        f"{ticker}<br>" +
                        "Date: %{x}<br>" +
                        "Close: $%{y:.2f}<br>" +
                        "Open: $%{customdata[0]:.2f}<br>" +
                        "High: $%{customdata[1]:.2f}<br>" +
                        "Low: $%{customdata[2]:.2f}<br>" +
                        "Volume: %{customdata[3]:,}<extra></extra>"
                    ),
                    customdata=data[['Open', 'High', 'Low', 'Volume']].values
                ))
                
                # Add moving averages
                if '20' in ma_options and 'MA20' in data:
                    fig.add_trace(go.Scatter(
                        x=data.index,
                        y=data['MA20'],
                        name=f"{ticker} 20-day MA",
                        line=dict(color=COLORS[i % len(COLORS)], dash='dash'),
                        opacity=0.5
                    ))
                if '50' in ma_options and 'MA50' in data:
                    fig.add_trace(go.Scatter(
                        x=data.index,
                        y=data['MA50'],
                        name=f"{ticker} 50-day MA",
                        line=dict(color=COLORS[i % len(COLORS)], dash='dot'),
                        opacity=0.5
                    ))
    
    # Update layout
    fig.update_layout(
        title=f'Stock Prices (Last {months} Months)',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        barmode='group' if chart_type == 'Bar' else 'overlay',
        xaxis_tickangle=-45,
        showlegend=True,
        height=600,
        margin=dict(b=200),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#1f2937')
    )
    
    return fig