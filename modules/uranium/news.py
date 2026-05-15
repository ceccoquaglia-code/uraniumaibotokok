"""
Modulo news — legge RSS feeds da fonti certificate (gratuito)
Fonti: World Nuclear News, IAEA, EIA, Mining.com, Trump/Truth Social, Reuters
"""

import feedparser
from datetime import datetime, timedelta, timezone
from config import URANIUM_NEWS_FEEDS, URANIUM_KEYWORDS, TRUMP_ENERGY_KEYWORDS


def get_news(hours_back: int = 24) -> list[dict]:
    """
    Scarica e filtra le news rilevanti dalle ultime N ore.
    Restituisce lista di articoli ordinati per rilevanza.
    """
    articles = []
    cutoff   = datetime.now(timezone.utc) - timedelta(hours=hours_back)

    for source_name, feed_url in URANIUM_NEWS_FEEDS.items():
        try:
            # feedparser gestisce automaticamente RSS e Atom
            feed = feedparser.parse(
                feed_url,
                request_headers={"User-Agent": "UraniumIntelligenceBot/1.0"}
            )

            for entry in feed.entries[:25]:
                title   = entry.get("title", "").strip()
                summary = entry.get("summary", "")[:400].strip()
                link    = entry.get("link", "")

                # Filtra per data se disponibile
                published = entry.get("published_parsed")
                if published:
                    try:
                        pub_dt = datetime(*published[:6], tzinfo=timezone.utc)
                        if pub_dt < cutoff:
                            continue
                    except Exception:
                        pass  # Se la data non è parsabile, includiamo comunque

                # Scegli le parole chiave in base alla fonte
                is_trump = "Trump" in source_name or "Truth" in source_name
                keywords = TRUMP_ENERGY_KEYWORDS if is_trump else URANIUM_KEYWORDS

                # Filtra per rilevanza
                text_combined = (title + " " + summary).lower()
                if not any(kw.lower() in text_combined for kw in keywords):
                    continue

                articles.append({
                    "source":   source_name,
                    "title":    title,
                    "summary":  summary,
                    "link":     link,
                    "is_trump": is_trump,
                    "relevance_score": _score_relevance(text_combined, keywords),
                })

        except Exception as e:
            print(f"⚠️  Errore feed '{source_name}': {e}")

    # Ordina per rilevanza e deduplica titoli simili
    articles.sort(key=lambda x: x["relevance_score"], reverse=True)
    articles = _deduplicate(articles)

    return articles[:12]  # Max 12 articoli


def _score_relevance(text: str, keywords: list) -> int:
    """Assegna un punteggio di rilevanza contando le keyword trovate"""
    return sum(1 for kw in keywords if kw.lower() in text)


def _deduplicate(articles: list) -> list:
    """Rimuove articoli con titoli quasi identici"""
    seen_words = set()
    unique     = []

    for article in articles:
        # Usa le prime 5 parole come fingerprint
        words = frozenset(article["title"].lower().split()[:5])
        if words not in seen_words:
            seen_words.add(words)
            unique.append(article)

    return unique
