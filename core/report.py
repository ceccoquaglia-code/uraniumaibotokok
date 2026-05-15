"""
Core Report — formatta i dati nel messaggio Telegram finale
"""

from datetime import datetime


def build_report(sector_name, sector_emoji, prices, news, signals, ai_result, score):
    """Costruisce il report giornaliero completo pronto per Telegram."""

    # Sezione prezzi
    price_lines = []
    for ticker, d in list(prices.items())[:6]:
        arrow = "▲" if d["change_pct"] > 0 else "▼"
        line = arrow + " <b>" + ticker + "</b>: $" + str(d["price"]) + " (" + str(d["change_pct"]) + "%)"
        price_lines.append(line)
    prices_block = "\n".join(price_lines) if price_lines else "Dati non disponibili"

    # Sezione segnali
    signal_lines = [s[0] + " " + s[1] + ": " + s[2] for s in signals]
    signals_block = "\n".join(signal_lines) if signal_lines else "Nessun segnale rilevante"

    # Sezione news
    news_lines = []
    for a in news[:4]:
        trump_tag = " USA" if a.get("is_trump") else ""
        news_lines.append("• <b>[" + a["source"] + "]</b>" + trump_tag + "\n  " + a["title"][:90])
    news_block = "\n".join(news_lines) if news_lines else "Nessuna news rilevante"

    # Score bar
    filled = score // 10
    score_bar = "█" * filled + "░" * (10 - filled)

    # Sentiment emoji
    sentiment_map = {"BULLISH": "🟢", "BEARISH": "🔴", "NEUTRALE": "⚪"}
    sent_emoji = sentiment_map.get(ai_result["sentiment"].upper(), "⚪")

    # Timestamp
    now = datetime.now().strftime("%d/%m/%Y - %H:%M")

    # Costruzione report riga per riga
    lines = []
    lines.append(sector_emoji + " <b>" + sector_name + " INTELLIGENCE</b>")
    lines.append("📅 " + now)
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append("💰 <b>PREZZI</b>")
    lines.append(prices_block)
    lines.append("")
    lines.append("📊 <b>SEGNALI</b>")
    lines.append(signals_block)
    lines.append("")
    lines.append("📰 <b>NEWS</b>")
    lines.append(news_block)
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append("🧠 <b>ANALISI AI</b>")
    lines.append(ai_result["analisi"])
    lines.append("")
    lines.append("⚠️ <i>Rischio: " + ai_result["rischio"] + "</i>")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append("📈 SCORE: <b>" + str(score) + "/100</b>")
    lines.append("<code>" + score_bar + "</code>")
    lines.append("")
    lines.append(sent_emoji + " Sentiment: <b>" + ai_result["sentiment"] + "</b>")
    lines.append("💡 <b>" + ai_result["azione"] + "</b>")
    lines.append("")
    lines.append("<i>\"" + ai_result["sintesi"] + "\"</i>")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append("💬 <i>Scrivi qualsiasi domanda per approfondire</i>")

    return "\n".join(lines)


def format_prices_only(prices):
    """Formatta solo i prezzi per il comando /prezzi"""
    if not prices:
        return "Impossibile scaricare i prezzi in questo momento."

    lines = ["💰 <b>PREZZI URANIO — Live</b>", ""]
    for ticker, d in prices.items():
        arrow = "▲" if d["change_pct"] > 0 else "▼"
        rsi = " | RSI " + str(d["rsi"]) if d.get("rsi") else ""
        lines.append(arrow + " <b>" + ticker + "</b> (" + d["name"] + ")")
        lines.append("   $" + str(d["price"]) + " (" + str(d["change_pct"]) + "%)" + rsi)

    lines.append("")
    lines.append("🕐 <i>Aggiornato: " + datetime.now().strftime("%H:%M") + "</i>")
    return "\n".join(lines)

