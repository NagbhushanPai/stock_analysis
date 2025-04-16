import plotly.graph_objects as go
from config.settings import COLORS
from ta.momentum import RSIIndicator
from ta.trend import MACD

def create_rl_chart(actions, net_worths, data, ticker, indicator_options):
    """
    Create a Plotly chart for RL trading performance.
    
    Args:
        actions (list): List of actions (0=hold, 1=buy, 2=sell).
        net_worths (list): List of net worths over time.
        data (pd.DataFrame): Stock data with index as dates.
        ticker (str): Stock ticker.
        indicator_options (list): Indicators to display ('RSI', 'MACD').
    
    Returns:
        go.Figure: Plotly figure object.
    """
    fig = go.Figure()
    
    # Plot closing prices
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        name=f"{ticker} Close",
        line=dict(color=COLORS[0])
    ))
    
    # Plot buy/sell markers
    buy_indices = [i for i, a in enumerate(actions) if a == 1]
    sell_indices = [i for i, a in enumerate(actions) if a == 2]
    
    fig.add_trace(go.Scatter(
        x=[data.index[i] for i in buy_indices],
        y=[data['Close'].iloc[i] for i in buy_indices],
        name="Buy",
        mode="markers",
        marker=dict(symbol="triangle-up", size=10, color="green")
    ))
    
    fig.add_trace(go.Scatter(
        x=[data.index[i] for i in sell_indices],
        y=[data['Close'].iloc[i] for i in sell_indices],
        name="Sell",
        mode="markers",
        marker=dict(symbol="triangle-down", size=10, color="red")
    ))
    
    # Plot net worth
    fig.add_trace(go.Scatter(
        x=data.index,
        y=net_worths,
        name="Net Worth",
        line=dict(color=COLORS[1], dash="dash"),
        yaxis="y2"
    ))
    
    # Plot indicators
    if 'RSI' in indicator_options:
        data['RSI'] = RSIIndicator(data['Close']).rsi()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['RSI'],
            name=f"{ticker} RSI",
            line=dict(color=COLORS[2]),
            yaxis="y3"
        ))
    
    if 'MACD' in indicator_options:
        macd = MACD(data['Close'])
        data['MACD'] = macd.macd()
        data['MACD_Signal'] = macd.macd_signal()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['MACD'],
            name=f"{ticker} MACD",
            line=dict(color=COLORS[3]),
            yaxis="y4"
        ))
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['MACD_Signal'],
            name=f"{ticker} MACD Signal",
            line=dict(color=COLORS[4], dash="dot"),
            yaxis="y4"
        ))
    
    # Update layout
    yaxes = {
        'yaxis': dict(title="Price (USD)", side="left"),
        'yaxis2': dict(title="Net Worth (USD)", overlaying="y", side="right")
    }
    if 'RSI' in indicator_options:
        yaxes['yaxis3'] = dict(title="RSI", anchor="free", overlaying="y", side="left", position=0.1, range=[0, 100])
    if 'MACD' in indicator_options:
        yaxes['yaxis4'] = dict(title="MACD", anchor="free", overlaying="y", side="right", position=0.9)
    
    fig.update_layout(
        title=f"{ticker} Trading Performance",
        xaxis_title="Date",
        **yaxes,
        xaxis_tickangle=-45,
        showlegend=True,
        height=800,
        margin=dict(b=200),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#1f2937')
    )
    
    return fig