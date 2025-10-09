def obtener_klines_binance(symbol="BTCUSDT", interval="1m", limit=100):
    """
    Obtiene las velas OHLC (Open, High, Low, Close) de Binance.
    Se usa para análisis técnico y cálculo de estructura TESLABTC A.P.
    """
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
        headers = {"User-Agent": "TESLABTC-API/1.0"}
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            print("⚠️ Error al obtener klines:", response.text)
            return None

        data = response.json()
        klines = [
            {
                "timestamp": k[0],
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5]),
            }
            for k in data
        ]
        return klines

    except Exception as e:
        print("⚠️ Error al obtener datos históricos de Binance:", e)
        return None
