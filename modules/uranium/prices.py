"""
Modulo prezzi — scarica dati azionari via Yahoo Finance API diretta
"""

import requests
from config import URANIUM_TICKERS

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

def get_prices():
    results = {}
    for ticker, name in URANIUM_TICKERS.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
            response = requests.get(url, headers=HEADERS, timeout=10)
            data = response.json()

            closes = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
            closes = [c for c in closes if c is not None]

            if len(closes) < 2:
                continue

            current = round(closes[-1], 2)
            prev = closes[-2]
            change_pct = round(((current - prev) / prev) * 100, 2)

            results[ticker] = {
                "name": name,
                "price": current,
                "change_pct": change_pct,
                "volume": 0,
                "volume_ratio": 1.0,
                "rsi": None,
                "week52_high": None,
                "week52_low": None,
            }
        except Exception as e:
            print(f"Errore prezzo {ticker}: {e}")

    return results
