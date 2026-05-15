"""
Modulo Uranio — orchestratore principale
Coordina raccolta dati, analisi AI e costruzione del report
"""

from .prices  import get_prices
from .news    import get_news
from .insider import get_insider_transactions
from .scorer  import calculate_score
from core.ai     import analyze_sector, chat_response
from core.report import build_report


async def get_uranium_report() -> str:
    """
    Genera il report completo del settore uranio.
    Chiamato automaticamente ogni mattina e da /report
    """

    # ── 1. Raccolta dati ──────────────────────────────────────────────────────
    prices  = get_prices()
    news    = get_news(hours_back=24)
    insider = get_insider_transactions(days_back=30)

    # ── 2. Prepara testi per l'AI ─────────────────────────────────────────────
    prices_text = _format_prices_for_ai(prices)
    news_text   = _format_news_for_ai(news)
    insider_text = _format_insider_for_ai(insider)

    # ── 3. Analisi AI (Groq, gratuito) ────────────────────────────────────────
    ai_result = analyze_sector(
        sector       = "uranio/nucleare",
        prices_text  = prices_text,
        news_text    = news_text,
        insider_text = insider_text,
    )

    # ── 4. Score tecnico ──────────────────────────────────────────────────────
    score, signals = calculate_score(prices, news, insider)

    # ── 5. Costruisci e restituisci il report formattato ──────────────────────
    return build_report(
        sector_name  = "URANIO",
        sector_emoji = "☢️",
        prices       = prices,
        news         = news,
        signals      = signals,
        ai_result    = ai_result,
        score        = score,
    )


async def get_uranium_chat_response(user_message: str) -> str:
    """
    Risponde a domande libere dell'utente con dati live.
    """
    prices = get_prices()
    news   = get_news(hours_back=48)

    prices_text = _format_prices_for_ai(prices)
    news_text   = _format_news_for_ai(news)

    return chat_response(
        sector        = "uranio/nucleare",
        prices_text   = prices_text,
        news_text     = news_text,
        user_question = user_message,
    )


# ── Helpers di formattazione per l'AI ────────────────────────────────────────

def _format_prices_for_ai(prices: dict) -> str:
    if not prices:
        return "Dati non disponibili"
    lines = []
    for ticker, d in prices.items():
        rsi_str = f"RSI {d['rsi']}" if d.get("rsi") else "RSI N/A"
        vol_str = f"Vol {d['volume_ratio']:.1f}x"
        lines.append(f"{ticker}: ${d['price']} ({d['change_pct']:+.1f}%) | {rsi_str} | {vol_str}")
    return "\n".join(lines)


def _format_news_for_ai(news: list) -> str:
    if not news:
        return "Nessuna news rilevante nelle ultime 24 ore"
    lines = [f"[{a['source']}] {a['title']}" for a in news[:10]]
    return "\n".join(lines)


def _format_insider_for_ai(insider: list) -> str:
    if not insider:
        return "Nessuna transazione insider recente"
    lines = [f"{t['ticker']}: Form 4 il {t['date']} ({t['days_ago']} giorni fa)" for t in insider]
    return "\n".join(lines)
