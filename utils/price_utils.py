def obtener_klines_binance(simbolo="BTCUSDT", intervalo="1h", limite=120):
    """
    Modo híbrido:
      1️⃣ Intenta Binance Vision
      2️⃣ Luego Binance REST
      3️⃣ Si ambos fallan → usa CoinGecko (simula klines con histórico de precios)
    """
    global BINANCE_STATUS
    urls = [
        f"{BINANCE_VISION_BASE}/api/v3/klines",
        f"{BINANCE_REST_BASE}/api/v3/klines",
    ]
    last_err = None

    # Binance Vision / REST
    for url in urls:
        try:
            r = requests.get(
                url,
                params={"symbol": simbolo, "interval": intervalo, "limit": limite},
                headers=UA, timeout=10,
            )
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list) and data:
                    src = "Vision" if "vision" in url else "REST"
                    BINANCE_STATUS = f"✅ Klines desde Binance {src}"
                    return data
            last_err = f"HTTP {r.status_code}"
        except Exception as e:
            last_err = str(e)

    # Fallback CoinGecko (simula klines)
    try:
        cg_interval = "daily" if "h" in intervalo else "hourly"
        r = requests.get(
            f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart",
            params={"vs_currency": "usd", "days": 7, "interval": cg_interval},
            headers=UA, timeout=10,
        )
        r.raise_for_status()
        data = r.json().get("prices", [])
        if data:
            BINANCE_STATUS = "🦎 Fallback CoinGecko (modo estimado)"
            klines = []
            for ts, price in data[-limite:]:
                open_ = close_ = high_ = low_ = price
                k = [ts, open_, high_, low_, close_, 0, ts, 0, 0, 0, 0, 0]
                klines.append(k)
            return klines
    except Exception as e:
        last_err = f"CoinGecko: {e}"

    BINANCE_STATUS = f"⛔ Sin datos válidos ({last_err})"
    return []
