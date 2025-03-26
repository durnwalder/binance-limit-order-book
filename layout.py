from dash import html, dcc

layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(
                    "Limit Order Book Bitcoin/USD Binance",
                    style={"text-align": "center", "color": "white", "margin": "10px 0"}
                )
            ],
            style={"backgroundColor": "black", "padding": "10px"}
        ),
        html.Div(
            children=[
                dcc.Graph(id="orderbook-histogram", style={"width": "1200px", "margin": "20px auto"})
            ]
        ),
        html.Div(
            children=[
                dcc.Graph(id="mid-price-chart", style={"width": "1200px", "margin": "20px auto"})
            ]
        ),
        dcc.Interval(id="timer", interval=3000)
    ],
    style={"backgroundColor": "black"}
)