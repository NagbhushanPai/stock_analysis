import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, ctx # Ensure ctx is imported
import plotly.graph_objs as go
from datetime import datetime, timedelta
from data.fetcher import fetch_historical_data
# Import necessary items from trainer
from rl.trainer import train_model, training_progress, training_eta, evaluate_model # Import evaluate_model
from rl.backtest import backtest_strategy, rsi_strategy
from rl.rl_visualizer import create_rl_chart
import os
import numpy as np
import time # Keep time import if needed elsewhere
import pandas as pd # Import pandas
import logging # Import the logging library

# --- Configure Logging ---
# Set up basic logging to ensure INFO messages (like SB3 summary) are shown
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s: %(message)s')
# You might want to adjust the format or level later if it becomes too verbose

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
                value=["RSI", "MACD"], # Default selected indicators
                inline=True, # Display inline
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
                n_clicks=0, # Initialize n_clicks
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 mb-2 mr-2" # Added margin
            ),
            html.Button(
                "Backtest RSI Strategy",
                id="backtest-btn",
                n_clicks=0, # Initialize n_clicks
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            ),
            # Progress Bar Container (initially hidden)
            html.Div(id="progress-container", children=[
                dbc.Progress(id="training-progress", value=0, max=100, striped=True, animated=True, className="mb-1"),
                html.Div(id="progress-text", className="text-center text-sm") # Smaller text
            ], style={"display": "none"}, className="mt-3") # Add margin top
        ], md=4),
        
        # Right: Charts and metrics
        dbc.Col([
            dcc.Graph(id="stock-chart", className="mb-4"),
            dcc.Graph(id="rl-chart", className="mb-4"),
            html.Div(id="metrics-output", className="text-center font-semibold") # Make metrics bold
        ], md=8)
    ]),
    dcc.Interval(
        id="progress-interval",
        interval=1000,  # Update every 1 second
        n_intervals=0,
        disabled=True # Start disabled
    )
], fluid=True)

# Callbacks
@app.callback(
    Output("stock-chart", "figure"),
    Input("ticker", "value"),
    Input("time-slider", "value"),
    Input("indicator-checklist", "value")
)
def update_stock_chart(ticker, months, indicators):
    # ... (existing stock chart logic - unchanged) ...
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        # Ensure context matches data usage if fetcher uses it
        data = fetch_historical_data(ticker, start_date, end_date, interval="1d", context="chart") 
        
        if data.empty:
            return go.Figure().update_layout(title=f"No data available for {ticker}", template="plotly_dark")
        
        fig = go.Figure()
        
        # Add stock price
        fig.add_trace(go.Scatter(
            x=data.index, y=data["Close"], mode="lines", name="Close Price", line=dict(color="#1f77b4") # Specific blue
        ))
        
        # Add indicators
        if "RSI" in indicators and "RSI" in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index, y=data["RSI"], mode="lines", name="RSI", line=dict(color="#2ca02c"), # Specific green
                yaxis="y2"
            ))
        if "MACD" in indicators and "MACD" in data.columns and "MACD_Signal" in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index, y=data["MACD"], mode="lines", name="MACD", line=dict(color="#d62728"), # Specific red
                yaxis="y3"
            ))
            fig.add_trace(go.Scatter(
                x=data.index, y=data["MACD_Signal"], mode="lines", name="MACD Signal", line=dict(color="#9467bd"), # Specific purple
                yaxis="y3"
            ))
        
        # Update layout for clarity
        fig.update_layout(
            title=f"{ticker} Stock Price and Indicators ({months} Months)",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            yaxis=dict(domain=[0.3, 1]), # Price takes top 70%
            yaxis2=dict(title="RSI", overlaying="y", side="right", anchor="free", position=1.0, range=[0, 100], showgrid=False),
            yaxis3=dict(title="MACD", anchor="x", overlaying="y", side="left", position=0.0, showgrid=False),
            xaxis=dict(domain=[0.0, 0.95]), # Make space for RSI axis
            template="plotly_dark", # Use dark theme
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=50, r=50, t=50, b=50) # Adjust margins
        )
        # Add range slider
        fig.update_xaxes(rangeslider_visible=True)

        return fig
    
    except Exception as e:
        print(f"Stock chart error: {str(e)}")
        return go.Figure().update_layout(title=f"Error loading chart: {str(e)}", template="plotly_dark")


@app.callback(
    [Output("rl-chart", "figure"),
     Output("metrics-output", "children"),
     Output("progress-container", "style"),
     Output("progress-interval", "disabled"),
     Output("training-progress", "value"),
     Output("progress-text", "children")],
    [Input("train-btn", "n_clicks"),
     Input("backtest-btn", "n_clicks"),
     Input("progress-interval", "n_intervals")], # Keep interval as input
    [State("rl-ticker", "value"),
     State("time-slider", "value"), # Use the main time slider for RL training period
     State("indicator-checklist", "value"), # Pass indicators to chart
     State("rl-algo", "value")],
    prevent_initial_call=True
)
def train_and_visualize_rl(n_train, n_backtest, n_intervals, ticker, months, indicator_options, algo):
    """
    Handles training, backtesting, and progress updates.
    Note: Synchronous training blocks UI. Progress updates via interval check global state.
    """
    triggered_id = ctx.triggered_id
    print(f"Callback triggered by: {triggered_id}")

    # Default outputs (no update unless changed)
    no_update = dash.no_update
    outputs = {
        "figure": no_update,
        "metrics": no_update,
        "progress_style": no_update,
        "interval_disabled": no_update,
        "progress_value": no_update,
        "progress_text": no_update,
    }

    # --- Handle Train Button Click ---
    if triggered_id == "train-btn":
        if not n_train or n_train == 0:
            return list(outputs.values()) # No action if n_clicks is 0 or None

        print(f"Train button clicked (n_clicks={n_train}). Starting training process...")
        # Show progress bar immediately and enable interval
        # This happens before the blocking call, but UI won't update until call finishes
        outputs["progress_style"] = {"display": "block"}
        outputs["progress_value"] = 0
        outputs["progress_text"] = "Initializing..."
        outputs["interval_disabled"] = False # Enable interval timer

        # Return these initial updates? No, Dash waits for the full callback.
        # The UI will likely show the *previous* state until training finishes.

        try:
            model_path = f"models/{algo}_{ticker}.zip"
            print(f"Calling train_model synchronously for {ticker} ({months} months)...")
            # This call blocks the server process
            actions, net_worths, total_reward, sharpe_ratio, max_drawdown = train_model(
                ticker, months=months, save_path=model_path, algo=algo, total_timesteps=50000 # Reduced for faster testing
            )
            print(f"train_model completed for {ticker}.")

            # --- Process results after training ---
            actions = [int(a.item()) if hasattr(a, 'item') else int(a) for a in actions]

            if not net_worths or not actions:
                 raise ValueError("Training returned empty actions or net_worths.")

            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            # Fetch data again for plotting
            data = fetch_historical_data(ticker, start_date, end_date, interval="1d", context="rl_chart")

            if data.empty:
                 raise ValueError(f"Failed to fetch data for chart for {ticker}")

            # Align lengths - crucial for plotting
            min_len = min(len(data), len(net_worths), len(actions))
            if len(data) > min_len: data = data.iloc[:min_len]
            if len(net_worths) > min_len: net_worths = net_worths[:min_len]
            if len(actions) > min_len: actions = actions[:min_len]

            if min_len == 0:
                 raise ValueError("No consistent data points after alignment.")

            print(f"Creating RL chart with {min_len} points.")
            fig = create_rl_chart(actions, net_worths, data, ticker, indicator_options)
            metrics = f"{algo.upper()} Results - Sharpe: {sharpe_ratio:.2f}, Max Drawdown: {max_drawdown:.2%}, Total Reward: {total_reward:.2f}"
            print(f"Returning final results. Metrics: {metrics}")

            # Update outputs for final state
            outputs["figure"] = fig
            outputs["metrics"] = metrics
            outputs["progress_style"] = {"display": "none"} # Hide progress bar
            outputs["interval_disabled"] = True # Disable interval
            outputs["progress_value"] = 100 # Show 100 briefly if needed
            outputs["progress_text"] = "Training completed!"

            return list(outputs.values())

        except Exception as e:
            print(f"Error during training or result processing: {str(e)}")
            error_fig = go.Figure().update_layout(title=f"Training Error: {str(e)}", template="plotly_dark")
            # Update outputs for error state
            outputs["figure"] = error_fig
            outputs["metrics"] = f"Error: {str(e)}"
            outputs["progress_style"] = {"display": "none"} # Hide progress bar
            outputs["interval_disabled"] = True # Disable interval
            outputs["progress_value"] = 0
            outputs["progress_text"] = "Training failed"
            return list(outputs.values())

    # --- Handle Progress Interval Tick ---
    elif triggered_id == "progress-interval":
        # This part updates the display based on global state from the trainer
        current_progress = training_progress # Read global variable
        current_eta = training_eta if training_eta is not None else "Calculating..." # Read global variable

        if 0 <= current_progress < 100:
            # Training is actively in progress (or just started)
            progress_text = f"Training... {current_progress}% (ETA: {current_eta})"
            # Keep progress bar visible, keep interval running, update values
            outputs["progress_style"] = {"display": "block"}
            outputs["interval_disabled"] = False
            outputs["progress_value"] = current_progress
            outputs["progress_text"] = progress_text
            # Don't update figure or metrics
            outputs["figure"] = no_update
            outputs["metrics"] = no_update
            return list(outputs.values())
        elif current_progress >= 100:
             # Training finished, interval should stop, hide progress bar
             # This state is mainly handled by the train-btn logic return,
             # but the interval might tick one last time.
             print("Interval detected completion (progress>=100). Disabling interval.")
             outputs["progress_style"] = {"display": "none"}
             outputs["interval_disabled"] = True
             outputs["progress_value"] = 100
             outputs["progress_text"] = "Finalizing..." # Or "Training completed!"
             # Don't update figure or metrics here
             outputs["figure"] = no_update
             outputs["metrics"] = no_update
             return list(outputs.values())
        else: # Progress is < 0 or invalid state? Should not happen.
             print("Interval update: Invalid progress state. Hiding progress.")
             outputs["progress_style"] = {"display": "none"}
             outputs["interval_disabled"] = True
             outputs["progress_value"] = 0
             outputs["progress_text"] = ""
             outputs["figure"] = no_update
             outputs["metrics"] = no_update
             return list(outputs.values())


    # --- Handle Backtest Button Click ---
    elif triggered_id == "backtest-btn":
        if not n_backtest or n_backtest == 0:
             return list(outputs.values())
        print(f"Backtest button clicked (n_clicks={n_backtest}). Running backtest...")
        try:
            result = backtest_strategy(ticker, months, rsi_strategy) # Assuming rsi_strategy is defined/imported
            if "error" in result:
                raise ValueError(result["error"])
            print(f"Backtest result: {result}")

            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            data = fetch_historical_data(ticker, start_date, end_date, interval="1d", context="backtest")

            if data.empty:
                 raise ValueError(f"No data for backtest chart for {ticker}")

            # Generate actions based on strategy for plotting
            actions = [rsi_strategy(data.iloc[:i+1]) for i in range(len(data))] # Assumes rsi_strategy takes data slice

            # Align lengths
            min_len = min(len(data), len(result["net_worths"]), len(actions))
            if len(data) > min_len: data = data.iloc[:min_len]
            net_worths = result["net_worths"][:min_len] # Use aligned net worths
            if len(actions) > min_len: actions = actions[:min_len]


            if min_len == 0:
                 raise ValueError("No consistent backtest data points after alignment.")

            fig = create_rl_chart(actions, net_worths, data, ticker, indicator_options)
            metrics = (
                f"RSI Strategy Results - Sharpe: {result['sharpe_ratio']:.2f}, "
                f"Max Drawdown: {result['max_drawdown']:.2%}"
            )
            print("Backtest visualization complete.")

            # --- Save results to CSV ---
            csv_dir = "CSV" # Defines the folder name
            os.makedirs(csv_dir, exist_ok=True) # Creates the folder if it doesn't exist
            timestamp = datetime.now().strftime("%H_%M_%S") # Format HH_MM_SS
            filename = f"Backtest Result {timestamp}.csv"
            filepath = os.path.join(csv_dir, filename) # Creates the full path

            # Create DataFrame with backtest results
            import pandas as pd
            metrics_df = pd.DataFrame({
                'Ticker': [ticker],
                'Strategy': ['RSI'],
                'Sharpe Ratio': [result['sharpe_ratio']],
                'Max Drawdown': [result['max_drawdown']],
                'Final Portfolio Value': [net_worths[-1] if len(net_worths) > 0 else 0],
                'Test Period (Months)': [months],
                'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            })
            metrics_df.to_csv(filepath, index=False)
            print(f"Backtest results saved to: {filepath}")
            # --- End Save results to CSV ---

            # Update outputs for backtest results
            outputs["figure"] = fig
            outputs["metrics"] = metrics
            outputs["progress_style"] = {"display": "none"} # Hide progress
            outputs["interval_disabled"] = True # Ensure interval is off
            outputs["progress_value"] = 0
            outputs["progress_text"] = ""
            return list(outputs.values())

        except Exception as e:
            print(f"Backtest error: {str(e)}")
            error_fig = go.Figure().update_layout(title=f"Backtest Error: {str(e)}", template="plotly_dark")
            # Update outputs for error state
            outputs["figure"] = error_fig
            outputs["metrics"] = f"Error: {str(e)}"
            outputs["progress_style"] = {"display": "none"}
            outputs["interval_disabled"] = True
            outputs["progress_value"] = 0
            outputs["progress_text"] = ""
            return list(outputs.values())

    # --- Default case or other triggers ---
    print(f"Callback triggered by unexpected source or no action needed: {triggered_id}")
    return list(outputs.values()) # Return default no_update


# Run server
if __name__ == "__main__":
    # Make sure models directory exists
    if not os.path.exists("models"):
        os.makedirs("models")
    print("Starting Dash server...")
    # Consider host='0.0.0.0' if running in a container or needs external access
    app.run(debug=True) # debug=True enables hot reloading and error pages