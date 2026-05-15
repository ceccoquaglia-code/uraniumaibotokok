"""
Modulo prezzi — scarica dati azionari via yfinance (gratuito)
Recupera: prezzo, variazione %, RSI, volume, posizione 52 settimane
"""

import yfinance as yf
import pandas as pd
from config import URANIUM_TICKERS


def get_prices() -> dict:
    """
    Scarica i prezzi aggiornati di tutti i ticker uranio.
    Restituisce un dizionario con tutti i dati tecnici.
    """
    results = {}

    for ticker, name in URANIUM_TICKERS.items():
        try:
            stock = yf.Ticker(ticker)

            # Ultimi 30 giorni per calcoli tecnici
            hist = stock.history(period="30d")

            if hist.empty or len(hist) < 2:
                continue

            # Prezzi base
            current_price = hist['Close'].iloc[-1]
            prev_close    = hist['Close'].iloc[-2]
            change_pct    = ((current_price - prev_close) / prev_close) * 100

            # Volume (confronto con media 20 giorni)
            today_volume  = hist['Volume'].iloc[-1]
            avg_volume    = hist['Volume'].rolling(20).mean().iloc[-1]
            volume_ratio  = today_volume / avg_volume if avg_volume > 0 else 1.0

            # RSI a 14 periodi
            rsi = _calculate_rsi(hist['Close'], period=14)

            # Posizione rispetto ai 52 settimane (da info)
            try:
                info          = stock.fast_info
                week52_high   = getattr(info, 'year_high', None)
                week52_low    = getattr(info, 'year_low', None)
            except Exception:
                week52_high = week52_low = None

            results[ticker] = {
                "name":         name,
                "price":        round(current_price, 2),
                "change_pct":   round(change_pct, 2),
                "volume":       int(today_volume),
                "volume_ratio": round(volume_ratio, 2),
                "rsi":          rsi,
                "week52_high":  round(week52_high, 2) if week52_high else None,
                "week52_low":   round(week52_low, 2)  if week52_low  else None,
            }

        except Exception as e:
            print(f"⚠️  Errore prezzo {ticker}: {e}")

    return results


def _calculate_rsi(prices: pd.Series, period: int = 14) -> float | None:
    """Calcola RSI classico a N periodi"""
    try:
        delta   = prices.diff().dropna()
        gain    = delta.clip(lower=0)
        loss    = (-delta).clip(lower=0)
        avg_gain = gain.rolling(period).mean().iloc[-1]
        avg_loss = loss.rolling(period).mean().iloc[-1]

        if avg_loss == 0:
            return 100.0
        rs  = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 1)
    except Exception:
        return None
