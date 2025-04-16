from dash import Dash, dcc, html, Input, Output
from components.plots import create_stock_bar_chart
from config.settings import TICKERS

app = Dash(__name__)

# Layout of the app
app.layout = html.Div([
    html.H1("Interactive Stock Price Bar Chart"),
    html.Label("Select Stocks:"),
    dcc.Checklist(
        id='stock-checklist',
        options=[{'label': ticker, 'value': ticker} for ticker in TICKERS],
        value=['NVDA'],  # Default to NVDA
        inline=True
    ),
    html.Label("Select Time Range (Months):", style={'marginTop': '20px'}),
    dcc.Slider(
        id='time-slider',
        min=1,
        max=12,
        step=1,
        value=6,  # Default to 6 months
        marks={i: f'{i}M' for i in range(1, 13)},
        tooltip={"placement": "bottom", "always_visible": True}
    ),
    dcc.Graph(id='stock-bar-chart')
])

# Callback to update the bar chart
@app.callback(
    Output('stock-bar-chart', 'figure'),
    [Input('stock-checklist', 'value'), Input('time-slider', 'value')]
)
def update_chart(selected_stocks, months):
    return create_stock_bar_chart(selected_stocks, months)

# Run the app
if __name__ == '__main__':
    print("Starting Dash server...")
    app.run(debug=True)