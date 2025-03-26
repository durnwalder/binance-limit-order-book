import math
from decimal import Decimal
from collections import deque
from datetime import datetime, timedelta

import pandas as pd
import requests
import plotly.graph_objects as go

import dash
from dash import Dash, html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc

app = Dash(external_stylesheets=[dbc.themes.CYBORG])

mid_price_history = deque()

def dropdown_option(title, options, default_value, _id):
    return html.Div(children=[
        html.H2(title),
        dcc.Dropdown(options=options, value=default_value, id=_id)
    ])

app.layout = html.Div(children=[
    html.Div(children=[
        html.Div(children=[
            dash_table.DataTable(
                id="ask_table",
                columns=[{"name": "Price", "id": "price"}, {"name": "Quantity", "id": "quantity"}],
                style_header={"display": "none"},
                style_cell={
                    "minWidth": "140px", "maxWidth": "140px", "width": "140px",
                    "text-align": "right"
                }
            ),
            html.H2(id="mid-price", style={"padding-top": "30px", "text-align": "center"}),
            dash_table.DataTable(
                id="bid_table",
                columns=[{"name": "Price", "id": "price"}, {"name": "Quantity", "id": "quantity"}],
                style_header={"display": "none"},
                style_cell={
                    "minWidth": "140px", "maxWidth": "140px", "width": "140px",
                    "text-align": "right"
                }
            )
        ], style={"width": "300px"}),
        html.Div(children=[
            dropdown_option("Aggregate Level", ["0.01", "0.1", "1", "10", "100"], "0.01", "aggregation-level"),
            dropdown_option("Pair", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BDOTDOT"], "ETHUSDT", "pair-select"),
            dropdown_option("Quantity Precision", ["0", "1", "2", "3", "4"], "2", "quantity-precision"),
            dropdown_option("Price Precision", ["0", "1", "2", "3", "4"], "2", "price-precision"),
        ], style={"padding-left": "100px"}),
    ], style={"display": "flex", "justify-content": "center", "align-items": "center", "height": "50vh"}),

    html.Div([
        dcc.Graph(id="orderbook-histogram", style={"width": "600px", "margin": "0 auto"})
    ]),

    html.Div([
        dcc.Graph(id="mid-price-chart", style={"width": "600px", "margin": "0 auto"})
    ]),

    dcc.Interval(id="timer", interval=3000)
])

def table_styling(df, side):
    if side == "ask":
        bar_color = "rgba(230, 31, 7, 0.2)"
        font_color = "rgb(230, 31, 7)"
    else:
        bar_color = "rgba(13, 230, 49, 0.2)"
        font_color = "rgb(13, 230, 49)"

    cell_bg_color = "#060606"
    n_bins = 25
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    quantity = df.quantity.astype(float)
    ranges = [((quantity.max() - quantity.min()) * i) + quantity.min() for i in bounds]

    styles = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        max_bound_percentage = bounds[i] * 100
        styles.append({
            "if": {
                "filter_query": (
                    "{{quantity}} >= {min_bound}"
                    + (" && {{quantity}} < {max_bound}" if (i < (len(bounds) - 1)) else "")
                ).format(min_bound=min_bound, max_bound=max_bound),
                "column_id": "quantity"
            },
            "background": (
                f"""
                linear-gradient(270deg,
                {bar_color} 0%,
                {bar_color} {max_bound_percentage}%,
                {cell_bg_color} {max_bound_percentage}%,
                {cell_bg_color} 100%)
                """
            ),
            "paddingBottom": 2,
            "paddingTop": 2,
        })
    styles.append({
        "if": {"column_id": "price"},
        "color": font_color,
        "background-color": cell_bg_color,
    })
    return styles

def aggregate_levels(levels_df, agg_level=Decimal('1'), side="bid"):
    if side == "bid":
        right = False
        label_func = lambda x: x.left
    else:
        right = True
        label_func = lambda x: x.right

    min_level = math.floor(Decimal(min(levels_df.price)) / agg_level - 1) * agg_level
    max_level = math.ceil(Decimal(max(levels_df.price)) / agg_level + 1) * agg_level
    level_bounds = [float(min_level + agg_level * x)
                    for x in range(int((max_level - min_level) / agg_level) + 1)]

    levels_df["bin"] = pd.cut(levels_df.price, bins=level_bounds, precision=10, right=right)
    grouped = levels_df.groupby("bin").agg(quantity=("quantity", "sum")).reset_index()
    grouped["price"] = grouped.bin.apply(label_func)
    grouped = grouped[grouped.quantity > 0]
    return grouped[["price", "quantity"]]

@app.callback(
    Output("bid_table", "data"),
    Output("bid_table", "style_data_conditional"),
    Output("ask_table", "data"),
    Output("ask_table", "style_data_conditional"),
    Output("mid-price", "children"),
    Output("orderbook-histogram", "figure"),
    Output("mid-price-chart", "figure"),
    Input("aggregation-level", "value"),
    Input("quantity-precision", "value"),
    Input("price-precision", "value"),
    Input("pair-select", "value"),
    Input("timer", "n_intervals")
)
def update_orderbook(agg_level, quantity_precision, price_precision, symbol, n_intervals):
    url = "https://api.binance.com/api/v3/depth"
    levels_to_show = 10
    params = {"symbol": symbol.upper(), "limit": 5000}
    data = requests.get(url, params=params).json()

    bid_df = pd.DataFrame(data["bids"], columns=["price", "quantity"], dtype=float)
    ask_df = pd.DataFrame(data["asks"], columns=["price", "quantity"], dtype=float)

    mid = (bid_df.price.iloc[0] + ask_df.price.iloc[0]) / 2
    mid_prec = int(quantity_precision) + 2
    mid_str = f"%.{mid_prec}f" % mid

    agg_bid_df = aggregate_levels(bid_df, agg_level=Decimal(agg_level), side="bid")
    agg_ask_df = aggregate_levels(ask_df, agg_level=Decimal(agg_level), side="ask")
    agg_bid_df = agg_bid_df.sort_values("price", ascending=False)
    agg_ask_df = agg_ask_df.sort_values("price", ascending=False)

    agg_bid_df = agg_bid_df.iloc[:levels_to_show]
    agg_ask_df = agg_ask_df.iloc[-levels_to_show:]

    bid_plot_df = agg_bid_df.copy()
    ask_plot_df = agg_ask_df.copy()

    agg_bid_df.quantity = agg_bid_df.quantity.apply(lambda x: f"%.{quantity_precision}f" % x)
    agg_bid_df.price = agg_bid_df.price.apply(lambda x: f"%.{price_precision}f" % x)
    agg_ask_df.quantity = agg_ask_df.quantity.apply(lambda x: f"%.{quantity_precision}f" % x)
    agg_ask_df.price = agg_ask_df.price.apply(lambda x: f"%.{price_precision}f" % x)

    bid_style = table_styling(agg_bid_df, "bid")
    ask_style = table_styling(agg_ask_df, "ask")

    bid_plot_df["price"] = bid_plot_df["price"].astype(float)
    bid_plot_df["quantity"] = bid_plot_df["quantity"].astype(float)
    ask_plot_df["price"] = ask_plot_df["price"].astype(float)
    ask_plot_df["quantity"] = ask_plot_df["quantity"].astype(float)

    fig_hist = go.Figure(layout=go.Layout(
        title=f"Aggregated Order Book Histogram: {symbol.upper()}",
        xaxis_title="Price",
        yaxis_title="Quantity",
    ))
    if not bid_plot_df.empty:
        fig_hist.add_trace(go.Bar(x=bid_plot_df["price"], y=bid_plot_df["quantity"], name="Bids"))
    if not ask_plot_df.empty:
        fig_hist.add_trace(go.Bar(x=ask_plot_df["price"], y=ask_plot_df["quantity"], name="Asks"))
    fig_hist.update_layout(barmode="group")

    now = datetime.now()
    mid_price_history.append((now, mid))
    cutoff = now - timedelta(minutes=3)
    while mid_price_history and mid_price_history[0][0] < cutoff:
        mid_price_history.popleft()

    times = [t[0] for t in mid_price_history]
    prices = [t[1] for t in mid_price_history]
    fig_line = go.Figure(layout=go.Layout(
        title=f"Last 3 Min Mid Price: {symbol.upper()}",
        xaxis_title="Time",
        yaxis_title="Mid Price"
    ))
    fig_line.add_trace(go.Scatter(x=times, y=prices, mode="lines", name="Mid Price"))

    return (
        agg_bid_df.to_dict("records"),
        bid_style,
        agg_ask_df.to_dict("records"),
        ask_style,
        mid_str,
        fig_hist,
        fig_line
    )

if __name__ == "__main__":
    app.run_server(debug=True)