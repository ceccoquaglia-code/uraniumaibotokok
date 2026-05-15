"""
╔══════════════════════════════════════════════════════════╗
║              CONFIGURAZIONE — config.py                  ║
║  Modifica qui le tue chiavi e preferenze                 ║
╚══════════════════════════════════════════════════════════╝

ISTRUZIONI:
- Non condividere mai questo file con nessuno
- Su Railway queste variabili si inseriscono nel pannello
  "Variables" — non serve modificare questo file
"""

import os

# ── TELEGRAM ──────────────────────────────────────────────────────────────────
# Ottieni il token da @BotFather su Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")

# Il tuo Chat ID personale (lo ottieni con @userinfobot su Telegram)
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ── GROQ AI (GRATUITO) ────────────────────────────────────────────────────────
# Registrati su console.groq.com e crea una API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Modello Groq da usare (gratuito, ottima qualità)
GROQ_MODEL = "llama-3.3-70b-versatile"

# ── ORARIO REPORT GIORNALIERO ─────────────────────────────────────────────────
# Formato HH:MM — il bot ti manda il report ogni mattina a quest'ora
REPORT_TIME = os.getenv("REPORT_TIME", "08:00")

# ── SOGLIE ALERT STRAORDINARI ─────────────────────────────────────────────────
# Il bot ti avvisa se un titolo si muove più di questa % in un'ora
ALERT_PRICE_THRESHOLD = float(os.getenv("ALERT_PRICE_THRESHOLD", "4.0"))

# ── MODULI ATTIVI ─────────────────────────────────────────────────────────────
# Per aggiungere un nuovo settore in futuro, aggiungi il nome qui
# e crea la cartella corrispondente in modules/
ACTIVE_MODULES = ["uranium"]  # Esempio futuro: ["uranium", "quantum", "defense"]

# ── TICKER MONITORATI ─────────────────────────────────────────────────────────
URANIUM_TICKERS = {
    "CCJ":  "Cameco Corp",
    "NXE":  "NexGen Energy",
    "UUUU": "Energy Fuels",
    "LEU":  "Centrus Energy",
    "DNN":  "Denison Mines",
    "URA":  "Global X Uranium ETF",
    "URNM": "Sprott Uranium Miners ETF",
    "SPUT": "Sprott Physical Uranium Trust",
}

# ── FONTI NEWS (RSS) ──────────────────────────────────────────────────────────
URANIUM_NEWS_FEEDS = {
    "World Nuclear News":   "https://www.world-nuclear-news.org/rss",
    "IAEA":                 "https://www.iaea.org/feeds/topstories.xml",
    "EIA":                  "https://www.eia.gov/rss/press_rss.xml",
    "Mining.com":           "https://www.mining.com/category/uranium/feed/",
    "Trump / Truth Social": "https://truthsocial.com/@realDonaldTrump.rss",
    "Reuters Energy":       "https://feeds.reuters.com/reuters/energy",
}

# ── PAROLE CHIAVE FILTRO NEWS ─────────────────────────────────────────────────
URANIUM_KEYWORDS = [
    "uranium", "nuclear", "reactor", "cameco", "kazatomprom",
    "enrichment", "SMR", "small modular", "yellowcake", "u3o8",
    "nexgen", "denison", "energy fuels", "nuclear energy",
    "nuclear power", "atomic", "fission", "centrus",
]

TRUMP_ENERGY_KEYWORDS = [
    "nuclear", "energy", "uranium", "power", "electricity",
    "russia", "kazakhstan", "sanction", "energy dominance",
    "drill", "lng", "oil",
]

# ── TICKER CIK SEC EDGAR (per insider trading) ────────────────────────────────
SEC_CIK_MAP = {
    "CCJ":  "0001009672",
    "NXE":  "0001404644",
    "UUUU": "0000315131",
    "LEU":  "0000098338",
}
