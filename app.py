import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
from datetime import datetime, timedelta
from data.fetcher import fetch_historical_data
from rl.trainer import train_model
from rl.backtest import backtest_strategy, rsi_strategy
from components.rl_visualizer import create_rl_chart
import os

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Stock Trading Visualizer"

# Constants
TICKERS = ["NVDA", "AAPL", "MSFT", "TSLA"]
DEFAULT_TICKER = "NVDA"

# Layout
app.layout = dbc.Container([
    html.H1("Stock Trading Visualizer", className="text-center my-4"),
    
    # Controls
    dbc.Row([
        # Left: Stock and RL controls
        dbc.Col([
            html.Label("Select Stock:", className="font-semibold mb-2"),
            dcc.Dropdown(
                id="ticker",
                options=[{"label": ticker, "value": ticker} for ticker in TICKERS],
                value=DEFAULT_TICKER,
                className="mb-4"
            ),
            html.Label("Time Range (Months):", className="font-semibold mb-2"),
            dcc.Slider(
                id="time-slider",
                min=1,
                max=24,
                step=1,
                value=12,
                marks={i: str(i) for i in [1, 6, 12, 18, 24]},
                className="mb-4"
            ),
            html.Label("Indicators:", className="font-semibold mb-2"),
            dcc.Checklist(
                id="indicator-checklist",
                options=[
                    {"label": "RSI", "value": "RSI"},
                    {"label": "MACD", "value": "MACD"}
                ],
                value=["RSI"],
                className="mb-4"
            ),
            html.Label("Train RL Model:", className="font-semibold mb-2"),
            dcc.Dropdown(
                id="rl-ticker",
                options=[{"label": ticker, "value": ticker} for ticker in TICKERS],
                value=DEFAULT_TICKER,
                className="mb-2"
            ),
            dcc.Dropdown(
                id="rl-algo",
                options=[
                    {"label": "PPO", "value": "ppo"},
                    {"label": "SAC", "value": "sac"}
                ],
                value="ppo",
                className="mb-2"
            ),
            html.Button(
                "Train Model",
                id="train-btn",
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 mb-2"
            ),
            html.Button(
                "Backtest RSI Strategy",
                id="backtest-btn",
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            )
        ], md=4),
        
        # Right: Charts and metrics
        dbc.Col([
            dcc.Graph(id="stock-chart", className="mb-4"),
            dcc.Graph(id="rl-chart", className="mb-4"),
            html.Div(id="metrics-output", className="text-center")
        ], md=8)
    ])
], fluid=True)

# Callbacks
@app.callback(
    Output("stock-chart", "figure"),
    Input("ticker", "value"),
    Input("time-slider", "value"),
    Input("indicator-checklist", "value")
)
def update_stock_chart(ticker, months, indicators):
    """
    Update the stock price chart with selected indicators.
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        data = fetch_historical_data(ticker, start_date, end_date, interval="1d", context="chart")
        
        if data.empty:
            raise ValueError(f"No data available for {ticker}")
        
        fig = go.Figure()
        
        # Add stock price
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["Close"],
            mode="lines",
            name="Close Price"
        ))
        
        # Add indicators
        if "RSI" in indicators:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data["RSI"],
                mode="lines",
                name="RSI",
                yaxis="y2"
            ))
        if "MACD" in indicators:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data["MACD"],
                mode="lines",
                name="MACD",
                yaxis="y3"
            ))
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data["MACD_Signal"],
                mode="lines",
                name="MACD Signal",
                yaxis="y3"
            ))
        
        # Update layout
        fig.update_layout(
            title=f"{ticker} Stock Price and Indicators",
            xaxis=dict(title="Date"),
            yaxis=dict(title="Price"),
            yaxis2=dict(title="RSI", overlaying="y", side="right", range=[0, 100]),
            yaxis3=dict(title="MACD", overlaying="y", side="left", position=0.05),
            template="plotly_dark"
        )
        
        return fig
    
    except Exception as e:
        return go.Figure().update_layout(
            title=f"Error loading chart: {str(e)}",
            template="plotly_dark"
        )

@app.callback(
    [Output("rl-chart", "figure"), Output("metrics-output", "children")],
    [Input("train-btn", "n_clicks"), Input("backtest-btn", "n_clicks")],
    [
        State("rl-ticker", "value"),
        State("time-slider", "value"),
        State("indicator-checklist", "value"),
        State("rl-algo", "value")
    ],
    prevent_initial_call=True
)
def train_and_visualize_rl(n_train, n_backtest, ticker, months, indicator_options, algo):
    """
    Train or backtest a model and visualize results.
    """
    if n_train:
        try:
            model_path = f"models/{algo}_{ticker}.zip"
            actions, net_worths, total_reward, sharpe_ratio, max_drawdown = train_model(
                ticker, months=months, save_path=model_path, algo=algo
            )
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            data = fetch_historical_data(ticker, start_date, end_date, interval="1d", context="rl")
            fig = create_rl_chart(actions, net_worths, data, ticker, indicator_options)
            metrics = f"{algo.upper()} - Sharpe Ratio: {sharpe_ratio:.2f}, Max Drawdown: {max_drawdown:.2%}, Total Reward: {total_reward:.2f}"
            return fig, metrics
        except Exception as e:
            return (
                go.Figure().update_layout(
                    title=f"Error training {algo.upper()} model: {str(e)}",
                    template="plotly_dark"
                ),
                f"Error: {str(e)}"
            )
    
    if n_backtest:
        try:
            result = backtest_strategy(ticker, months, rsi_strategy)
            if "error" in result:
                raise ValueError(result["error"])
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            data = fetch_historical_data(ticker, start_date, end_date, interval="1d", context="backtest")
            actions = [rsi_strategy(data.iloc[:i+1]) for i in range(len(data))]
            fig = create_rl_chart(actions, result["net_worths"], data, ticker, indicator_options)
            metrics = (
                f"RSI Strategy - Sharpe Ratio: {result['sharpe_ratio']:.2f}, "
                f"Max Drawdown: {result['max_drawdown']:.2%}"
            )
            return fig, metrics
        except Exception as e:
            return (
                go.Figure().update_layout(
                    title=f"Error backtesting RSI strategy: {str(e)}",
                    template="plotly_dark"
                ),
                f"Error: {str(e)}"
            )
    
    return dash.no_update, dash.no_update

# Run server
if __name__ == "__main__":
    print("Starting Dash server...")
    app.run(debug=True)