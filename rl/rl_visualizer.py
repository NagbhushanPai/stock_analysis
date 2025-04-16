import plotly.graph_objs as go

def create_rl_chart(actions, net_worths, data, ticker, indicators):
    """
    Create a chart showing stock price, net worth, actions, and indicators.
    """
    try:
        fig = go.Figure()

        # Add Close price
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["Close"],
            mode="lines",
            name="NVDA Close",
            line=dict(color="blue")
        ))

        # Add Net Worth
        fig.add_trace(go.Scatter(
            x=data.index[:len(net_worths)],
            y=net_worths,
            mode="lines",
            name="Net Worth",
            line=dict(color="orange", dash="dash"),
            yaxis="y2"
        ))

        # Add Buy/Sell markers
        buy_indices = [i for i, a in enumerate(actions) if a == 1]
        sell_indices = [i for i, a in enumerate(actions) if a == 2]
        fig.add_trace(go.Scatter(
            x=[data.index[i] for i in buy_indices],
            y=[net_worths[i] for i in buy_indices],
            mode="markers",
            name="Buy",
            marker=dict(symbol="triangle-up", size=10, color="red")
        ))
        fig.add_trace(go.Scatter(
            x=[data.index[i] for i in sell_indices],
            y=[net_worths[i] for i in sell_indices],
            mode="markers",
            name="Sell",
            marker=dict(symbol="triangle-down", size=10, color="green")
        ))

        # Add indicators
        if "RSI" in indicators:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data["RSI"],
                mode="lines",
                name="NVDA RSI",
                line=dict(color="lightgreen"),
                yaxis="y3"
            ))
        if "MACD" in indicators:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data["MACD"],
                mode="lines",
                name="NVDA MACD",
                line=dict(color="darkgreen"),
                yaxis="y4"
            ))
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data["MACD_Signal"],
                mode="lines",
                name="NVDA MACD Signal",
                line=dict(color="purple"),
                yaxis="y4"
            ))

        # Update layout with multiple y-axes
        fig.update_layout(
            title=f"{ticker} Trading Performance",
            xaxis=dict(title="Date"),
            yaxis=dict(title="Price (USD)", domain=[0.3, 1.0]),
            yaxis2=dict(title="Net Worth (USD)", overlaying="y", side="right", position=0.85, range=[0, 8000], domain=[0.3, 1.0]),
            yaxis3=dict(title="RSI", overlaying="y", side="right", position=0.75, range=[0, 100], domain=[0.0, 0.25]),
            yaxis4=dict(title="MACD", overlaying="y", side="right", position=0.65, range=[-10, 10], domain=[0.0, 0.25]),
            template="plotly_dark",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        return fig

    except Exception as e:
        print(f"Chart creation error: {str(e)}")
        return go.Figure().update_layout(
            title=f"Error creating chart: {str(e)}",
            template="plotly_dark"
        )