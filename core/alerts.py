"""
Core Alerts — sistema di alert straordinari
Controlla ogni ora se ci sono eventi che meritano una notifica immediata,
indipendentemente dal report giornaliero.
"""

import json
import os
from datetime import datetime, timedelta
from modules.uranium.prices import get_prices
from modules.uranium.news   import get_news
from config import ALERT_PRICE_THRESHOLD


# File per ricordare quali alert sono già stati inviati (evita duplicati)
SENT_ALERTS_FILE = "sent_alerts.json"


def _load_sent_alerts() -> dict:
    if os.path.exists(SENT_ALERTS_FILE):
        try:
            with open(SENT_ALERTS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_sent_alert(alert_key: str):
    alerts = _load_sent_alerts()
    alerts[alert_key] = datetime.now().isoformat()
    # Pulisci alert più vecchi di 24 ore
    cutoff = datetime.now() - timedelta(hours=24)
    alerts = {
        k: v for k, v in alerts.items()
        if datetime.fromisoformat(v) > cutoff
    }
    with open(SENT_ALERTS_FILE, "w") as f:
        json.dump(alerts, f)


def _already_sent(alert_key: str) -> bool:
    return alert_key in _load_sent_alerts()


async def check_alerts() -> str | None:
    """
    Controlla se ci sono condizioni che richiedono un alert immediato.
    Restituisce il messaggio dell'alert se c'è, altrimenti None.

    Condizioni di alert:
    1. Un ticker si muove più del threshold in un giorno
    2. News critica da fonte istituzionale
    """

    alert_messages = []

    # ── Alert prezzi ──────────────────────────────────────────────────────────
    try:
        prices = get_prices()
        for ticker, data in prices.items():
            change = abs(data.get("change_pct", 0))
            if change >= ALERT_PRICE_THRESHOLD:
                direction = "🚀 SALITA" if data["change_pct"] > 0 else "📉 DISCESA"
                alert_key = f"price_{ticker}_{datetime.now().strftime('%Y%m%d')}"

                if not _already_sent(alert_key):
                    alert_messages.append(
                        f"⚡ <b>{ticker} — {direction} SIGNIFICATIVA</b>\n"
                        f"Variazione: {data['change_pct']:+.1f}% oggi\n"
                        f"Prezzo: ${data['price']}"
                    )
                    _save_sent_alert(alert_key)
    except Exception as e:
        print(f"⚠️  Errore check prezzi per alert: {e}")

    # ── Alert news critiche ────────────────────────────────────────────────────
    try:
        news = get_news(hours_back=2)  # Solo ultime 2 ore
        critical_keywords = [
            "production cut", "shutdown", "ban", "sanction",
            "emergency", "breakthrough", "major deal", "acquisition",
            "taglio produzione", "accordo", "miliardi",
        ]

        for article in news[:5]:
            title_lower = article["title"].lower()
            is_critical = any(kw in title_lower for kw in critical_keywords)

            if is_critical:
                alert_key = f"news_{hash(article['title']) % 100000}"
                if not _already_sent(alert_key):
                    alert_messages.append(
                        f"📰 <b>NEWS CRITICA — {article['source']}</b>\n"
                        f"{article['title']}"
                    )
                    _save_sent_alert(alert_key)
    except Exception as e:
        print(f"⚠️  Errore check news per alert: {e}")

    # ── Componi messaggio finale ───────────────────────────────────────────────
    if not alert_messages:
        return None

    header  = "🚨 <b>ALERT STRAORDINARIO — URANIO</b>\n"
    header += f"🕐 {datetime.now().strftime('%H:%M del %d/%m/%Y')}\n\n"
    body    = "\n\n".join(alert_messages)
    footer  = "\n\n💬 <i>Scrivi /report per l'analisi completa</i>"

    return header + body + footer
