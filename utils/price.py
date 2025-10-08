import requests

BINANCE_URL = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
COINBASE_URL = "https://api.coinbase.com/v2/prices/BTC-USD/spot"

def get_btc_price():
    # Intenta Binance
    try:
        r = requests.get(BINANCE_URL, timeout=10)
        if r.status_code == 200:
            return float(r.json()["price"])
    except Exception:
        pass
    # Backup Coinbase
    try:
        r = requests.get(COINBASE_URL, timeout=10)
        if r.status_code == 200:
            return float(r.json()["data"]["amount"])
    except Exception:
        pass
    return None
