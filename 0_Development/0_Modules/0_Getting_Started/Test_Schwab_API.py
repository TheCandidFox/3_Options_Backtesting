import requests
import time
import datetime
import csv

# === CONFIGURATION ===
TD_API_KEY = "YOUR_TD_API_KEY"
ACCESS_TOKEN = "YOUR_OAUTH_BEARER_TOKEN"
BASE_URL = "https://api.tdameritrade.com/v1"

# Define your option input
TICKER = "GOOGL"
STRIKE = 167
DAYS_TO_EXPIRY = 6
CALL_PUT = "put"  # or "call"

# Output CSV filename
FILENAME = f"{TICKER}_{STRIKE}_{CALL_PUT}_{DAYS_TO_EXPIRY}d.csv"

# === STEP 1: Find Expiration Date ===
def get_expiration_date(days_out):
    today = datetime.date.today()
    future_date = today + datetime.timedelta(days=days_out)
    return future_date.strftime("%Y-%m-%d")

# === STEP 2: Find Option Contract ===
def find_option_contract():
    exp_date = get_expiration_date(DAYS_TO_EXPIRY)
    url = f"{BASE_URL}/marketdata/chains"
    params = {
        "apikey": TD_API_KEY,
        "symbol": TICKER,
        "contractType": CALL_PUT.upper(),
        "strike": STRIKE,
        "fromDate": exp_date,
        "toDate": exp_date,
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    
    # Parse and find the exact option symbol
    option_chain = data.get("putExpDateMap" if CALL_PUT == "put" else "callExpDateMap")
    if not option_chain:
        raise Exception("No contracts found")

    for expiry in option_chain:
        for strike in option_chain[expiry]:
            contract = option_chain[expiry][strike][0]
            return contract["symbol"]  # This is the full OCC option symbol

    raise Exception("No matching contract")

# === STEP 3: Get Real-Time Quote ===
def get_option_quote(symbol):
    url = f"{BASE_URL}/marketdata/{symbol}/quotes"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    resp = requests.get(url, headers=headers)
    data = resp.json()
    if symbol not in data:
        raise Exception("Quote not found")
    quote = data[symbol]
    bid = quote.get("bid", 0)
    ask = quote.get("ask", 0)
    last = quote.get("last", 0)
    mid = round((bid + ask) / 2, 4) if bid and ask else last
    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "symbol": symbol,
        "bid": bid,
        "ask": ask,
        "mid": mid,
        "last": last,
        "volume": quote.get("totalVolume", 0)
    }

# === STEP 4: Track Every Minute ===
def track_option(symbol):
    with open(FILENAME, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "symbol", "bid", "ask", "mid", "last", "volume"])
        writer.writeheader()
        try:
            while True:
                data = get_option_quote(symbol)
                print(data)
                writer.writerow(data)
                f.flush()
                time.sleep(60)
        except KeyboardInterrupt:
            print("Tracking stopped.")

# === MAIN EXECUTION ===
if __name__ == "__main__":
    contract_symbol = find_option_contract()
    print(f"Tracking: {contract_symbol}")
    track_option(contract_symbol)
