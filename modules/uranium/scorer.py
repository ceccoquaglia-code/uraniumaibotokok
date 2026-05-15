"""
Motore di scoring — calcola lo score 0-100 del settore uranio
basandosi su segnali tecnici, fondamentali e di flusso.

I pesi sono calibrati per riflettere l'importanza relativa
di ogni segnale nel settore uranio/nucleare.
"""


def calculate_score(prices: dict, news: list, insider: list) -> tuple[int, list]:
    """
    Calcola lo score e la lista dei segnali rilevati.

    Returns:
        (score: int 0-100, signals: list of (emoji, label, detail))
    """
    score   = 50  # Base neutra
    signals = []

    # ── 1. MOMENTUM PREZZI (fino a ±20 punti) ─────────────────────────────────
    if prices:
        changes = [
            d["change_pct"]
            for d in prices.values()
            if d.get("change_pct") is not None
        ]
        if changes:
            avg_change = sum(changes) / len(changes)

            if avg_change > 4:
                score += 20
                signals.append(("🟢", "Momentum forte",    f"Settore +{avg_change:.1f}% oggi"))
            elif avg_change > 1.5:
                score += 10
                signals.append(("🟢", "Momentum positivo", f"Settore +{avg_change:.1f}% oggi"))
            elif avg_change > 0:
                score += 4
                signals.append(("🟡", "Momentum debole",   f"Settore +{avg_change:.1f}% oggi"))
            elif avg_change < -4:
                score -= 20
                signals.append(("🔴", "Vendite forti",     f"Settore {avg_change:.1f}% oggi"))
            elif avg_change < -1.5:
                score -= 10
                signals.append(("🔴", "Momentum negativo", f"Settore {avg_change:.1f}% oggi"))
            else:
                score -= 4
                signals.append(("⚪", "Momentum flat",     f"Settore {avg_change:.1f}% oggi"))

    # ── 2. RSI (fino a ±15 punti) ─────────────────────────────────────────────
    ccj_data = prices.get("CCJ", {})
    rsi      = ccj_data.get("rsi")

    if rsi is not None:
        if rsi < 30:
            score += 15
            signals.append(("🟢", "RSI ipervenduto",  f"RSI CCJ: {rsi} → possibile rimbalzo"))
        elif rsi < 45:
            score += 7
            signals.append(("🟡", "RSI zona acquisto", f"RSI CCJ: {rsi}"))
        elif rsi > 75:
            score -= 15
            signals.append(("🔴", "RSI ipercomprato",  f"RSI CCJ: {rsi} → attenzione eccesso"))
        elif rsi > 60:
            score -= 5
            signals.append(("🟡", "RSI elevato",       f"RSI CCJ: {rsi}"))
        else:
            signals.append(("⚪", "RSI neutrale",      f"RSI CCJ: {rsi}"))

    # ── 3. VOLUME ANOMALO (fino a +10 punti) ──────────────────────────────────
    vol_ratio = ccj_data.get("volume_ratio", 1.0)

    if vol_ratio > 2.0:
        score += 10
        signals.append(("🟢", "Volume molto alto",  f"CCJ: {vol_ratio:.1f}x la media → forte interesse"))
    elif vol_ratio > 1.4:
        score += 5
        signals.append(("🟡", "Volume elevato",     f"CCJ: {vol_ratio:.1f}x la media"))
    elif vol_ratio < 0.6:
        score -= 5
        signals.append(("⚪", "Volume basso",       f"CCJ: {vol_ratio:.1f}x la media → scarso interesse"))

    # ── 4. POSIZIONE 52 SETTIMANE (fino a ±10 punti) ──────────────────────────
    price_52h = ccj_data.get("week52_high")
    price_52l = ccj_data.get("week52_low")
    price_now = ccj_data.get("price")

    if price_52h and price_52l and price_now:
        range_52 = price_52h - price_52l
        if range_52 > 0:
            position = (price_now - price_52l) / range_52  # 0 = min, 1 = max

            if position < 0.25:
                score += 10
                signals.append(("🟢", "Vicino ai minimi annuali",  f"CCJ a {position*100:.0f}% del range 52w"))
            elif position > 0.85:
                score -= 8
                signals.append(("🔴", "Vicino ai massimi annuali", f"CCJ a {position*100:.0f}% del range 52w"))
            else:
                signals.append(("⚪", "Posizione 52w neutra",      f"CCJ a {position*100:.0f}% del range 52w"))

    # ── 5. INSIDER ACTIVITY (fino a +10 punti) ────────────────────────────────
    if insider:
        recenti = [t for t in insider if t.get("days_ago", 99) <= 14]
        if recenti:
            score += 10
            signals.append(("🟢", "Insider attivi",
                            f"{len(recenti)} transazione/i Form 4 negli ultimi 14 giorni"))
        else:
            score += 5
            signals.append(("🟡", "Insider activity",
                            f"{len(insider)} transazione/i nell'ultimo mese"))

    # ── 6. NEWS VOLUME (fino a ±5 punti) ──────────────────────────────────────
    trump_news = [a for a in news if a.get("is_trump")]
    if trump_news:
        score += 5
        signals.append(("🟢", "Trump menziona energia/nucleare",
                        f"{len(trump_news)} post recente/i su Truth Social"))

    # ── CLAMP finale ──────────────────────────────────────────────────────────
    score = max(0, min(100, score))

    return score, signals
