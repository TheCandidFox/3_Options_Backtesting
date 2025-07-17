# ========================== Imports ==========================
import os
import sys
from datetime import datetime, timedelta
from collections.abc import Mapping, Container

import pandas as pd
import plotly.graph_objects as go
from polygon import RESTClient

# ===================== Path Setup for Shared Code =====================
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Shared_Functions import Options_Utils as mine

# ===================== API Setup =====================
keys = mine.load_secrets()
API_KEY = keys["POLYGON_REST_API_KEY"]
client = RESTClient(api_key=API_KEY)


# ===================== Utility Functions =====================
def aggs_to_dataframe(aggs: list) -> pd.DataFrame:
    """Convert list of Polygon Agg objects into a clean pandas DataFrame."""
    if not aggs:
        return pd.DataFrame()
    
    data = [{
        "datetime": datetime.fromtimestamp(a.timestamp / 1000),
        "open": a.open,
        "high": a.high,
        "low": a.low,
        "close": a.close,
        "volume": a.volume,
        "vwap": a.vwap,
        "transactions": a.transactions,
        "otc": a.otc,
        "raw_timestamp": a.timestamp
    } for a in aggs]
    
    df = pd.DataFrame(data)
    df.set_index("datetime", inplace=True)
    return df


def deep_getsizeof(obj, seen=None):
    """Recursively calculates total memory usage of an object, including nested elements."""
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)
    size = sys.getsizeof(obj)
    
    if isinstance(obj, dict):
        size += sum((deep_getsizeof(k, seen) + deep_getsizeof(v, seen)) for k, v in obj.items())
    elif isinstance(obj, (list, tuple, set, frozenset)):
        size += sum(deep_getsizeof(i, seen) for i in obj)
    return size

def daterange_chunks(start: str, end: str, chunk_days: int = 30):
    """Yield date ranges in chunks (for paginated API safety)."""
    start_dt = datetime.strptime(start, "%Y-%m-%d")
    end_dt = datetime.strptime(end, "%Y-%m-%d")
    
    while start_dt < end_dt:
        chunk_end = min(start_dt + timedelta(days=chunk_days), end_dt)
        yield start_dt.strftime("%Y-%m-%d"), chunk_end.strftime("%Y-%m-%d")
        start_dt = chunk_end
        
def run_pipeline(ticker, start_date, end_date, timespan="minute", multiplier=1):
    for chunk_start, chunk_end in daterange_chunks(start_date, end_date):
        print(f"Processing {ticker} from {chunk_start} to {chunk_end}...")

        # Load
        aggs = list(client.list_aggs(
            ticker=ticker,
            multiplier=multiplier,
            timespan=timespan,
            from_=chunk_start,
            to=chunk_end,
            limit=50000
        ))

        # Process
        df = aggs_to_dataframe(aggs)

        # Optional: Analyze
        # df = my_signal_engine(df)  # placeholder for custom logic

        # Store
        filename = f"data/{ticker}_{chunk_start}_{chunk_end}_{timespan}.csv"
        os.makedirs("data", exist_ok=True)
        df.to_csv(filename)
        print(f"Saved {len(df)} rows to {filename}")

# ===================== Main Execution =====================
if __name__ == "__main__":
    # Configuration
    ticker = "AAPL"
    timespan = "hour"
    start_date = "2024-12-01"
    end_date = "2024-12-02"

    # Load aggregate bars
    aggs = list(client.list_aggs(
        ticker=ticker,
        multiplier=1,
        timespan=timespan,
        from_=start_date,
        to=end_date,
        limit=50000
    ))

    # Convert to DataFrame
    df = aggs_to_dataframe(aggs)

    # Diagnostics
    print(df.head())
    print(f"Number of aggregate bars: {len(aggs)}")
    print(f"Total memory used by 'aggs': {deep_getsizeof(aggs) / 1024:.2f} KB")
    print(type(aggs[0]))
    print(aggs[0])
    print(dir(aggs[0]))






# Testing out how to visualize or graph the information pulled into the aggs.
'''
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
'''





