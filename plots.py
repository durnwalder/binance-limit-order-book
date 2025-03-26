import numpy as np
import plotly.graph_objects as go

_cached_y_range = None

def calculate_height(mid, prices):
    global _cached_y_range
    if _cached_y_range is not None:
        return _cached_y_range
    if prices:
        y_min_val = min(prices)
        y_max_val = max(prices)
        delta = y_max_val - y_min_val
        computed_range = 2 * delta
        max_range = 0.05 * mid
        height = computed_range if computed_range < max_range else max_range
        if height <= 0:
            height = mid / 100
        _cached_y_range = [mid - height / 2, mid + height / 2]
    else:
        _cached_y_range = [mid - mid / 200, mid + mid / 200]
    return _cached_y_range

def plot_limit_order_book(symbol, bid_plot_df, ask_plot_df):
    fig = go.Figure(layout=go.Layout(
        xaxis_title="Price",
        yaxis_title="Quantity",
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white"),
        xaxis=dict(tickfont=dict(color="white")),
        yaxis=dict(tickfont=dict(color="white"))
    ))
    if not bid_plot_df.empty:
        fig.add_trace(go.Bar(
            x=bid_plot_df["price"],
            y=bid_plot_df["quantity"],
            name="Bids",
            width=10,
            marker=dict(color="green")
        ))
    if not ask_plot_df.empty:
        fig.add_trace(go.Bar(
            x=ask_plot_df["price"],
            y=ask_plot_df["quantity"],
            name="Asks",
            width=10,
            marker=dict(color="red")
        ))
    fig.update_layout(barmode="group")
    return fig

def plot_mid_price_chart(symbol, times, prices, cutoff, now, y_range, mid_str):
    fig = go.Figure(layout=go.Layout(
        title=f"Last 3 Min Mid Price: {symbol} - {mid_str}",
        xaxis_title="Time",
        yaxis_title="Mid Price",
        xaxis_range=[cutoff, now],
        yaxis_range=y_range,
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white"),
        xaxis=dict(tickfont=dict(color="white")),
        yaxis=dict(tickfont=dict(color="white"))
    ))
    fig.add_trace(go.Scatter(
        x=times,
        y=prices,
        mode="lines+markers",
        name="Mid Price",
        line=dict(width=3, color="deepskyblue"),
        marker=dict(symbol="circle", size=10, color="deepskyblue")
    ))
    return fig