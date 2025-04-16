from dash import Dash, dcc, html, Input, Output, State, callback_context
from components.plots import create_stock_chart
from config.settings import TICKERS, CHART_TYPES
from utils.helpers import generate_csv_download
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[
    'https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css',
    '/static/styles.css'
])

# Layout with enhanced UI
app.layout = html.Div(className='min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors duration-300', children=[
    # Header
    html.Div(className='flex justify-between items-center p-4 bg-blue-600 dark:bg-blue-800 text-white', children=[
        html.H1('Interactive Stock Visualizer', className='text-2xl font-bold'),
        html.Button('Toggle Dark Mode', id='dark-mode-toggle', className='px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded')
    ]),
    
    # Main content
    html.Div(className='container mx-auto p-4', children=[
        # Controls
        html.Div(className='grid grid-cols-1 md:grid-cols-2 gap-4 mb-4', children=[
            # Stock selection
            html.Div([
                html.Label('Select Stocks:', className='font-semibold mb-2'),
                dcc.Checklist(
                    id='stock-checklist',
                    options=[{'label': ticker, 'value': ticker} for ticker in TICKERS],
                    value=['NVDA'],
                    inline=True,
                    className='space-x-4'
                )
            ]),
            # Chart type and moving averages
            html.Div([
                html.Label('Chart Type:', className='font-semibold mb-2'),
                dcc.RadioItems(
                    id='chart-type',
                    options=[{'label': ct, 'value': ct} for ct in CHART_TYPES],
                    value='Bar',
                    inline=True,
                    className='space-x-4'
                ),
                html.Label('Show Moving Averages:', className='font-semibold mt-4 mb-2'),
                dcc.Checklist(
                    id='ma-checklist',
                    options=[{'label': '20-day MA', 'value': '20'}, {'label': '50-day MA', 'value': '50'}],
                    value=[],
                    inline=True,
                    className='space-x-4'
                )
            ])
        ]),
        
        # Time slider
        html.Label('Select Time Range (Months):', className='font-semibold mb-2'),
        dcc.Slider(
            id='time-slider',
            min=1,
            max=12,
            step=1,
            value=6,
            marks={i: f'{i}M' for i in range(1, 13)},
            tooltip={'placement': 'bottom', 'always_visible': True},
            className='mb-4'
        ),
        
        # Error message
        html.Div(id='error-message', className='text-red-500 mb-4 hidden'),
        
        # Chart and export button
        dcc.Loading(
            id='loading',
            type='circle',
            children=[
                dcc.Graph(id='stock-chart', className='bg-white dark:bg-gray-800 p-4 rounded shadow'),
                html.Button('Download Data as CSV', id='download-btn', className='mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700'),
                dcc.Download(id='download-csv')
            ]
        ),
        
        # Interval for real-time updates
        dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0)  # Update every 60 seconds
    ])
])

# Callback for dark mode toggle
@app.callback(
    Output('dark-mode-toggle', 'children'),
    Input('dark-mode-toggle', 'n_clicks'),
    State('dark-mode-toggle', 'children')
)
def toggle_dark_mode(n_clicks, current_text):
    if n_clicks:
        return 'Toggle Light Mode' if current_text == 'Toggle Dark Mode' else 'Toggle Dark Mode'
    return current_text

# Callback for chart update
@app.callback(
    [Output('stock-chart', 'figure'), Output('error-message', 'children'), Output('error-message', 'className')],
    [Input('stock-checklist', 'value'), Input('time-slider', 'value'), 
     Input('chart-type', 'value'), Input('ma-checklist', 'value'),
     Input('interval-component', 'n_intervals')]
)
def update_chart(selected_stocks, months, chart_type, ma_options, n_intervals):
    error_msg = ""
    error_class = 'text-red-500 mb-4 hidden'
    
    try:
        fig = create_stock_chart(selected_stocks, months, chart_type, ma_options)
        if not fig.data:
            error_msg = "No data available for selected stocks. Please try different stocks or check your connection."
            error_class = 'text-red-500 mb-4'
    except Exception as e:
        error_msg = f"Error fetching data: {str(e)}"
        error_class = 'text-red-500 mb-4'
        fig = go.Figure()
    
    return fig, error_msg, error_class

# Callback for CSV download
@app.callback(
    Output('download-csv', 'data'),
    Input('download-btn', 'n_clicks'),
    State('stock-checklist', 'value'),
    State('time-slider', 'value'),
    prevent_initial_call=True
)
def download_csv(n_clicks, selected_stocks, months):
    if n_clicks:
        return generate_csv_download(selected_stocks, months)
    return None

# Run the app
if __name__ == '__main__':
    print("Starting Dash server...")
    app.run(debug=True)