import math
from decimal import Decimal
from collections import deque
from datetime import datetime, timedelta
import numpy as np

import pandas as pd
import requests
import plotly.graph_objects as go

from dash import Dash, Input, Output
import dash_bootstrap_components as dbc

from plots import plot_limit_order_book, plot_mid_price_chart, calculate_height
from layout import layout 

app = Dash(external_stylesheets=[dbc.themes.CYBORG], title="Limit Order Book Bitcoin/USD Binance")
app.layout = layout

mid_price_history = deque()

fixed_bin_edges = None

def fixed_aggregate_levels(df, mid):
    global fixed_bin_edges
    if fixed_bin_edges is None:
        lower = mid - 10 * 50   # 50 bins below
        upper = mid + 10 * 50   # 50 bins above
        fixed_bin_edges = np.arange(lower, upper + 10, 10)  # 100 bins of width 10
    df = df.copy()
    df["bin"] = pd.cut(df["price"], bins=fixed_bin_edges, right=False)
    grouped = df.groupby("bin").agg(quantity=("quantity", "sum")).reset_index()
    grouped["price"] = grouped["bin"].apply(lambda b: b.left + 5 if pd.notnull(b) else None)
    bin_centers = fixed_bin_edges[:-1] + 5
    full = pd.DataFrame({"price": bin_centers})
    full = full.merge(grouped[["price", "quantity"]], on="price", how="left").fillna(0)
    return full


def get_data_from_binance():
    symbol = "BTCUSDT"
    quantity_precision = "2"
    
    url = "https://api.binance.com/api/v3/depth"
    params = {"symbol": symbol.upper(), "limit": 5000}
    data = requests.get(url, params=params).json()
    
    bid_df = pd.DataFrame(data["bids"], columns=["price", "quantity"], dtype=float)
    ask_df = pd.DataFrame(data["asks"], columns=["price", "quantity"], dtype=float)
    
    mid = (bid_df.price.iloc[0] + ask_df.price.iloc[0]) / 2
    mid_prec = int(quantity_precision) + 2
    mid_str = f"%.{mid_prec}f" % mid
    return symbol, bid_df, ask_df, mid, mid_str



@app.callback(
    Output("orderbook-histogram", "figure"),
    Output("mid-price-chart", "figure"),
    Input("timer", "n_intervals")
)
def update_orderbook(n_intervals):
    # Get data from Binance using the helper method.
    symbol, bid_df, ask_df, mid, mid_str = get_data_from_binance()
    
    bid_plot_df = fixed_aggregate_levels(bid_df, mid)
    ask_plot_df = fixed_aggregate_levels(ask_df, mid)
    
    fig_hist = plot_limit_order_book(symbol, bid_plot_df, ask_plot_df)
    
    now = datetime.now()
    mid_price_history.append((now, mid))
    cutoff = now - timedelta(minutes=3)
    
    while mid_price_history and mid_price_history[0][0] < cutoff:
        mid_price_history.popleft()
    
    times = [t[0] for t in mid_price_history]
    prices = [t[1] for t in mid_price_history]
    y_range = calculate_height(mid, prices)
    
    fig_line = plot_mid_price_chart(symbol, times, prices, cutoff, now, y_range, mid_str)
    
    return fig_hist, fig_line

if __name__ == "__main__":
    app.run_server(debug=True)