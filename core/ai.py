"""
Core AI — interfaccia con Groq API (gratuito)
Modello: llama-3.3-70b-versatile
Gestisce sia i report automatici che la chat interattiva
"""

from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

# Client Groq (gratuito, veloce)
_client = Groq(api_key=GROQ_API_KEY)


def analyze_sector(
    sector: str,
    prices_text: str,
    news_text: str,
    insider_text: str,
) -> dict:
    """
    Analisi AI completa per il report giornaliero.
    Restituisce un dizionario con tutti i campi del report.
    """

    prompt = f"""Sei un analista finanziario esperto nel settore {sector}.
Fornisci un'analisi professionale basata esclusivamente sui dati forniti.

═══ PREZZI ATTUALI ═══
{prices_text}

═══ NEWS ULTIME 24H ═══
{news_text}

═══ ATTIVITÀ INSIDER ═══
{insider_text}

Traduci in italiano i titoli delle news se sono in inglese.
Rispondi SOLO con questo formato esatto (non aggiungere altro testo):

[ANALISI] (2-3 frasi su cosa sta succedendo nel mercato)
[SENTIMENT] (solo una parola: BULLISH oppure BEARISH oppure NEUTRALE)
[AZIONE] (scegli UNA: "🚀 Opportunità" / "👀 Tieni posizione" / "⏸️ Aspetta" / "⚠️ Attenzione" / "🔴 Riduci")
[RISCHIO] (1 frase sul rischio più importante da monitorare)
[SINTESI] (1 frase finale, massimo 15 parole)"""

    try:
        response = _client.chat.completions.create(
            model       = GROQ_MODEL,
            messages    = [{"role": "user", "content": prompt}],
            max_tokens  = 400,
            temperature = 0.2,  # Bassa temperatura = risposte più coerenti e precise
        )
        raw = response.choices[0].message.content
        return _parse_analysis(raw)

    except Exception as e:
        print(f"⚠️  Errore Groq API: {e}")
        return _fallback_analysis()


def chat_response(
    sector: str,
    prices_text: str,
    news_text: str,
    user_question: str,
) -> str:
    """
    Risposta in modalità chat — risponde a domande libere dell'utente.
    """

    prompt = f"""Sei un analista finanziario esperto nel settore {sector}.
Rispondi alla domanda dell'utente usando i dati disponibili.

═══ DATI LIVE ═══
PREZZI: {prices_text}

NEWS RECENTI: {news_text}

═══ DOMANDA UTENTE ═══
{user_question}

Regole di risposta:
- Traduci in italiano qualsiasi titolo o testo in inglese che citi
- Sii specifico e cita i dati quando rilevante  
- Non dare mai consigli finanziari assoluti: usa termini probabilistici
- Massimo 250 parole
- Se non hai dati sufficienti per rispondere, dillo chiaramente"""

    try:
        response = _client.chat.completions.create(
            model       = GROQ_MODEL,
            messages    = [{"role": "user", "content": prompt}],
            max_tokens  = 500,
            temperature = 0.4,
        )
        answer = response.choices[0].message.content.strip()
        return f"🤖 <b>Analisi AI</b>\n\n{answer}"

    except Exception as e:
        print(f"⚠️  Errore Groq API chat: {e}")
        return "⚠️ Servizio AI temporaneamente non disponibile. Riprova tra qualche minuto."


# ── Helpers interni ───────────────────────────────────────────────────────────

def _parse_analysis(raw_text: str) -> dict:
    """Estrae i campi strutturati dalla risposta AI"""
    result = {
        "analisi":   "",
        "sentiment": "NEUTRALE",
        "azione":    "⏸️ Aspetta",
        "rischio":   "",
        "sintesi":   "",
    }

    for line in raw_text.strip().split("\n"):
        line = line.strip()
        if line.startswith("[ANALISI]"):
            result["analisi"]   = line.replace("[ANALISI]", "").strip()
        elif line.startswith("[SENTIMENT]"):
            result["sentiment"] = line.replace("[SENTIMENT]", "").strip().upper()
        elif line.startswith("[AZIONE]"):
            result["azione"]    = line.replace("[AZIONE]", "").strip()
        elif line.startswith("[RISCHIO]"):
            result["rischio"]   = line.replace("[RISCHIO]", "").strip()
        elif line.startswith("[SINTESI]"):
            result["sintesi"]   = line.replace("[SINTESI]", "").strip()

    return result


def _fallback_analysis() -> dict:
    """Risposta di emergenza se l'AI non risponde"""
    return {
        "analisi":   "Analisi AI non disponibile in questo momento.",
        "sentiment": "NEUTRALE",
        "azione":    "⏸️ Aspetta",
        "rischio":   "Verifica manualmente i dati.",
        "sintesi":   "Servizio AI temporaneamente offline.",
    }
