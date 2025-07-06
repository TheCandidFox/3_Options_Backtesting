from polygon import RESTClient
import plotly.graph_objects as go
from datetime import datetime

client = RESTClient(api_key="qkfxp0JUT_a24IQODdlWvZLBs0DIrNtb")


ticker = "AAPL"

# List Aggregates (Bars)
aggs = []
for a in client.list_aggs(ticker=ticker, multiplier=1, timespan="hour", from_="2024-12-01", to="2024-12-02", limit=50000):
    aggs.append(a)


timestamps = [datetime.fromtimestamp(bar.timestamp / 1000) for bar in aggs]
opens = [bar.open for bar in aggs]
highs = [bar.high for bar in aggs]
lows = [bar.low for bar in aggs]
closes = [bar.close for bar in aggs]
volumes = [bar.volume for bar in aggs]


fig = go.Figure(data=[go.Candlestick(
    x=timestamps,
    open=opens,
    high=highs,
    low=lows,
    close=closes
)])

fig.update_layout(title='Candlestick Chart', xaxis_title='Time', yaxis_title='Price')
fig.write_html("chart.html")






# Additional Information on how to access trades + quotes
'''
# Get Last Trade
trade = client.get_last_trade(ticker=ticker)
print(trade)

# List Trades
trades = client.list_trades(ticker=ticker, timestamp="2024-01-04")
for trade in trades:
    print(trade)

# Get Last Quote
quote = client.get_last_quote(ticker=ticker)
print(quote)

# List Quotes
quotes = client.list_quotes(ticker=ticker, timestamp="2024-01-04")
for quote in quotes:
    print(quote)
'''