import os
import json
import pandas as pd
from datetime import datetime

def load_secrets():
    secrets_path = os.path.join(os.path.dirname(__file__), 'secrets.json')
    if not os.path.exists(secrets_path):
        raise FileNotFoundError(f"Secrets file not found at {secrets_path}")

    with open(secrets_path, 'r') as f:
        return json.load(f)

# Not operational yet, using just locally in rest polygon
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
