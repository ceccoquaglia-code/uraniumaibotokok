"""
Core Report — formatta i dati nel messaggio Telegram finale
Produce output leggibile in 30 secondi, ottimizzato per mobile
"""

from datetime import datetime


def build_report(
    sector_name:  str,
    sector_emoji: str,
    prices:       dict,
    news:         list,
    signals:      list,
    ai_result:    dict,
    score:        int,
) -> str:
    """
    Costruisce il report giornaliero completo pronto per Telegram.
    """

    # ── Sezione prezzi ────────────────────────────────────────────────────────
    price_lines = []
    for ticker, d in list(prices.items())[:6]:
        arrow = "▲" if d["change_pct"] > 0 else "▼"
        price_lines.append(
            f"{arrow} <b>{ticker}</b>: ${d['price']} ({d['change_pct']:+.1f}%)"
        )
    prices_block = "\n".join(price_lines) if price_lines else "Dati non disponibili"

    # ── Sezione segnali tecnici ───────────────────────────────────────────────
    signal_lines = [f"{s[0]} {s[1]}: {s[2]}" for s in signals]
    signals_block = "\n".join(signal_lines) if signal_lines else "⚪ Nessun segnale rilevante"

    # ── Sezione news (max 4) ──────────────────────────────────────────────────
    news_lines = []
    for a in news[:4]:
        trump_tag = " 🇺🇸" if a.get("is_trump") else ""
        news_lines.append(f"• <b>[{a['source']}]</b>{trump_tag}\n  {a['title'][:90]}")
    news_block = "\n".join(news_lines) if news_lines else "Nessuna news rilevante"

    # ── Score bar visiva ──────────────────────────────────────────────────────
    filled    = score // 10
    score_bar = "█" * filled + "░" * (10 - filled)

    # ── Sentiment emoji ───────────────────────────────────────────────────────
    sentiment_map = {"BULLISH": "🟢", "BEARISH": "🔴", "NEUTRALE": "⚪"}
    sent_emoji    = sentiment_map.get(ai_result["sentiment"].upper(), "⚪")

    # ── Timestamp ─────────────────────────────────────────────────────────────
    now = datetime.now().strftime("%d/%m/%Y • %H:%M")

    # ── Report finale ─────────────────────────────────────────────────────────
    report = (
        f"{sector_emoji} <b>{sector_name} INTELLIGENCE</b>\n"
        f"📅 {now}\n\n"

        f"━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>PREZZI</b>\n"
        f"{prices_block}\n\n"

        f"📊 <b>SEGNALI</b>\n"
        f"{signals_block}\n\n"

        f"📰 <b>NEWS</b>\n"
        f"{news_block}\n\n"

        f"━━━━━━━━━━━━━━━━━━\n"
        f"🧠 <b>ANALISI AI</b>\n"
        f"{ai_result['analisi']}\n\n"
        f"⚠️ <i>Rischio: {ai_result['rischio']}</i>\n\n"

        f"━━━━━━━━━━━━━━━━━━\n"
        f"📈 SCORE: <b>{score}/100</b>\n"
        f"<code>{score_bar}</code>\n\n"
        f"{sent_emoji} Sentiment: <b>{ai_result['sentiment']}</b>\n"
        f"💡 <b>{ai_result['azione']}</b>\n\n"
        f"<i>"{ai_result['sintesi']}"</i>\n\n"

        f"━━━━━━━━━━━━━━━━━━\n"
        f"💬 <i>Scrivi qualsiasi domanda per approfondire</i>\n"
        f"<i>Es: \"Perché questo score?\" • \"Analisi CCJ\"</i>"
    )

    return report


def format_prices_only(prices: dict) -> str:
    """Formatta solo i prezzi (per comando /prezzi)"""
    if not prices:
        return "⚠️ Impossibile scaricare i prezzi in questo momento."

    lines = ["💰 <b>PREZZI URANIO — Live</b>\n"]
    for ticker, d in prices.items():
        arrow = "▲" if d["change_pct"] > 0 else "▼"
        rsi   = f" | RSI {d['rsi']}" if d.get("rsi") else ""
        h52   = f" | Max52w: ${d['week52_high']}" if d.get("week52_high") else ""
        lines.append(
            f"{arrow} <b>{ticker}</b> ({d['name']})\n"
            f"   ${d['price']} ({d['change_pct']:+.1f}%){rsi}{h52}"
        )

    lines.append(f"\n🕐 <i>Aggiornato: {datetime.now().strftime('%H:%M')}</i>")
    return "\n".join(lines)
