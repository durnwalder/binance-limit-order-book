# Limit Order Book Bitcoin/USD Binance

Playing around with Dash to display a live order book for Binance. This simple web application retrieves real-time data from the Binance API and shows:

1. **Order Book Histogram:** Histogram of bids and asks.
2. **Mid-Price Chart:** The evolution of the BTC/USD mid-price over the last three minutes.

![Screenshot](screenshot.png)

## Requirements

- Python 3.8+
- Dash, Dash Bootstrap Components, Plotly, Pandas, Requests
## Installation

This project manages packages using [PIXI](https://github.com/prefix-dev/pixi).
To install Pixi on macOS and Linux, open a terminal and run the following command:
   ```bash
    curl -fsSL https://pixi.sh/install.sh | bash
    # or with brew
    brew install pixi
   ```

   Run the following command to install all dependencies:
   
   ```bash
   pixi install
   ```

## Usage

   To start the binance order book dashboard run:
   
   ```bash
   pixi run binance
   ```


Then open [http://localhost:8050](http://localhost:8050) in your browser to view the live dashboard.