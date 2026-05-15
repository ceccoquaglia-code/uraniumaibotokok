"""
Modulo insider trading — legge Form 4 da SEC EDGAR (gratuito, ufficiale)
I Form 4 segnalano acquisti/vendite di azioni da parte di dirigenti aziendali
"""

import requests
from datetime import datetime, timedelta
from config import SEC_CIK_MAP


# SEC richiede un User-Agent identificativo nelle richieste
SEC_HEADERS = {
    "User-Agent": "UraniumIntelligenceBot research@example.com",
    "Accept-Encoding": "gzip, deflate",
}


def get_insider_transactions(days_back: int = 30) -> list[dict]:
    """
    Scarica le transazioni insider (Form 4) degli ultimi N giorni
    per i principali ticker uranio da SEC EDGAR.
    """
    transactions = []
    cutoff       = datetime.now() - timedelta(days=days_back)

    for ticker, cik in SEC_CIK_MAP.items():
        try:
            # API SEC EDGAR — completamente gratuita
            url      = f"https://data.sec.gov/submissions/CIK{cik}.json"
            response = requests.get(url, headers=SEC_HEADERS, timeout=15)

            if response.status_code != 200:
                continue

            data     = response.json()
            filings  = data.get("filings", {}).get("recent", {})

            forms      = filings.get("form", [])
            dates      = filings.get("filingDate", [])
            accessions = filings.get("accessionNumber", [])

            for i, form in enumerate(forms):
                if form != "4":  # Solo Form 4 (insider transactions)
                    continue

                try:
                    filing_date = datetime.strptime(dates[i], "%Y-%m-%d")
                except ValueError:
                    continue

                if filing_date < cutoff:
                    continue

                # Costruisci URL diretto al documento SEC
                acc_clean = accessions[i].replace("-", "")
                sec_url   = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=4&dateb=&owner=include&count=10"

                transactions.append({
                    "ticker":      ticker,
                    "date":        dates[i],
                    "form":        form,
                    "description": "Transazione insider (acquisto/vendita dirigenti)",
                    "url":         sec_url,
                    "days_ago":    (datetime.now() - filing_date).days,
                })

        except Exception as e:
            print(f"⚠️  Errore insider SEC {ticker}: {e}")

    # Ordina per data più recente
    transactions.sort(key=lambda x: x["date"], reverse=True)

    return transactions[:8]
