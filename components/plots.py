import plotly.graph_objects as go
from datetime import datetime, timedelta
from data.fetcher import fetch_historical_data
from config.settings import TICKERS, COLORS
from ta.momentum import RSIIndicator
from ta.trend import MACD

def create_stock_chart(selected_stocks, months, chart_type, ma_options, indicator_options):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)
    interval = "1m" if months <= 1 else "1d"
    fig = go.Figure()
    
    for i, ticker in enumerate(selected_stocks):
        if ticker in TICKERS:
            data = fetch_historical_data(ticker, start_date, end_date, interval=interval, context="chart")
            if not data.empty:
                data['RSI'] = RSIIndicator(data['Close']).rsi()
                macd = MACD(data['Close'])
                data['MACD'] = macd.macd()
                data['MACD_Signal'] = macd.macd_signal()
                
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
                
                if 'RSI' in indicator_options:
                    fig.add_trace(go.Scatter(
                        x=data.index,
                        y=data['RSI'],
                        name=f"{ticker} RSI",
                        line=dict(color=COLORS[(i+1) % len(COLORS)]),
                        yaxis="y2"
                    ))
                
                if 'MACD' in indicator_options:
                    fig.add_trace(go.Scatter(
                        x=data.index,
                        y=data['MACD'],
                        name=f"{ticker} MACD",
                        line=dict(color=COLORS[(i+2) % len(COLORS)]),
                        yaxis="y3"
                    ))
                    fig.add_trace(go.Scatter(
                        x=data.index,
                        y=data['MACD_Signal'],
                        name=f"{ticker} MACD Signal",
                        line=dict(color=COLORS[(i+3) % len(COLORS)], dash="dot"),
                        yaxis="y3"
                    ))
    
    fig.update_layout(
        title=f'Stock Prices (Last {months} Months)',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        yaxis2=dict(title="RSI", overlaying="y", side="right", range=[0, 100]) if 'RSI' in indicator_options else {},
        yaxis3=dict(title="MACD", anchor="free", overlaying="y", side="left", position=0.1) if 'MACD' in indicator_options else {},
        barmode='group' if chart_type == 'Bar' else 'overlay',
        xaxis_tickangle=-45,
        showlegend=True,
        height=800,
        margin=dict(b=200),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#1f2937')
    )
    
    return fig