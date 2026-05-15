"""
╔══════════════════════════════════════════════════════════╗
║         URANIUM INTELLIGENCE BOT — main.py              ║
║  Entry point: avvia il bot Telegram e lo scheduler       ║
╚══════════════════════════════════════════════════════════╝
"""

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, REPORT_TIME
from modules.uranium import get_uranium_report, get_uranium_chat_response
from core.alerts import check_alerts

# ── LOGGING ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ── COMANDI TELEGRAM ──────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Messaggio di benvenuto"""
    await update.message.reply_text(
        "☢️ <b>URANIUM INTELLIGENCE BOT</b>\n\n"
        "Ciao! Sono il tuo assistente finanziario per il settore uranio.\n\n"
        "<b>Cosa puoi chiedermi:</b>\n"
        "• /report → Report completo adesso\n"
        "• /analisi CCJ → Analisi specifica su un titolo\n"
        "• /help → Tutti i comandi\n\n"
        "Oppure scrivimi qualsiasi domanda libera:\n"
        "<i>\"Perché CCJ sta salendo?\"\n"
        "\"Vale la pena comprare NXE oggi?\"\n"
        "\"Cosa è successo al Kazakistan questa settimana?\"</i>",
        parse_mode='HTML'
    )

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista comandi"""
    await update.message.reply_text(
        "📋 <b>COMANDI DISPONIBILI</b>\n\n"
        "/report — Report completo uranio\n"
        "/analisi [TICKER] — Analisi specifica (es: /analisi CCJ)\n"
        "/prezzi — Solo i prezzi aggiornati\n"
        "/news — Solo le ultime news\n"
        "/insider — Attività insider recente\n"
        "/help — Questo messaggio\n\n"
        "💬 Puoi anche scrivere qualsiasi domanda libera!",
        parse_mode='HTML'
    )

async def cmd_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Genera report completo on-demand"""
    msg = await update.message.reply_text("⏳ Raccolta dati in corso...")
    report = await get_uranium_report()
    await msg.edit_text(report, parse_mode='HTML')

async def cmd_analisi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Analisi specifica su un ticker"""
    if context.args:
        ticker = context.args[0].upper()
        msg = await update.message.reply_text(f"🔍 Analizzo {ticker}...")
        response = await get_uranium_chat_response(f"Analisi dettagliata del titolo {ticker}: prezzo attuale, trend, RSI, news recenti, vale la pena considerarlo?")
        await msg.edit_text(response, parse_mode='HTML')
    else:
        await update.message.reply_text("❌ Specifica un ticker. Esempio: /analisi CCJ")

async def cmd_prezzi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Solo i prezzi aggiornati"""
    from modules.uranium.prices import get_prices
    from core.report import format_prices_only
    msg = await update.message.reply_text("⏳ Scarico prezzi...")
    prices = get_prices()
    text = format_prices_only(prices)
    await msg.edit_text(text, parse_mode='HTML')

async def cmd_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Solo le ultime news"""
    from modules.uranium.news import get_news
    msg = await update.message.reply_text("⏳ Leggo le fonti...")
    news = get_news(hours_back=24)
    if not news:
        await msg.edit_text("📰 Nessuna news rilevante nelle ultime 24 ore.")
        return
    lines = [f"• <b>[{a['source']}]</b>\n  {a['title']}" for a in news[:8]]
    text = "📰 <b>NEWS URANIO — Ultime 24h</b>\n\n" + "\n\n".join(lines)
    await msg.edit_text(text, parse_mode='HTML')

async def cmd_insider(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("⏳ Consulto SEC EDGAR...")
    try:
        insider = get_insider_transactions()
        if not insider:
            await msg.edit_text("👔 Nessuna transazione insider rilevante nell'ultimo mese.")
            return
        lines = [f"• <b>{t['ticker']}</b>: {t['type']} — {t['date']}" for t in insider]
        text = "👔 <b>INSIDER TRANSACTIONS — Ultimi 30gg</b>\n\n" + "\n".join(lines)
        await msg.edit_text(text, parse_mode='HTML')
    except Exception:
        await msg.edit_text("⚠️ SEC EDGAR non risponde in questo momento. Riprova tra qualche minuto.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce messaggi liberi dell'utente — modalità chat"""
    user_message = update.message.text
    msg = await update.message.reply_text("🤔 Analizzo...")
    response = await get_uranium_chat_response(user_message)
    await msg.edit_text(response, parse_mode='HTML')


# ── REPORT E ALERT AUTOMATICI ─────────────────────────────────────────────────

async def send_daily_report(app: Application):
    """Invia il report giornaliero automatico"""
    logger.info("📊 Generando report giornaliero...")
    try:
        report = await get_uranium_report()
        await app.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=report,
            parse_mode='HTML'
        )
        logger.info("✅ Report giornaliero inviato")
    except Exception as e:
        logger.error(f"❌ Errore report giornaliero: {e}")

async def check_and_send_alerts(app: Application):
    """Controlla e invia alert straordinari ogni ora"""
    try:
        alert = await check_alerts()
        if alert:
            await app.bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=alert,
                parse_mode='HTML'
            )
            logger.info("🚨 Alert straordinario inviato")
    except Exception as e:
        logger.error(f"❌ Errore controllo alert: {e}")


# ── AVVIO BOT ─────────────────────────────────────────────────────────────────

def main():
    # Costruisci applicazione Telegram
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Registra comandi
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("report", cmd_report))
    app.add_handler(CommandHandler("analisi", cmd_analisi))
    app.add_handler(CommandHandler("prezzi", cmd_prezzi))
    app.add_handler(CommandHandler("news", cmd_news))
    app.add_handler(CommandHandler("insider", cmd_insider))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Scheduler per report automatici
    scheduler = AsyncIOScheduler()

    # Report giornaliero all'orario configurato
    hour, minute = REPORT_TIME.split(":")
    scheduler.add_job(
        send_daily_report,
        trigger='cron',
        hour=int(hour),
        minute=int(minute),
        args=[app]
    )

    # Controllo alert ogni ora
    scheduler.add_job(
        check_and_send_alerts,
        trigger='interval',
        hours=1,
        args=[app]
    )

    scheduler.start()

    logger.info(f"🤖 Bot avviato! Report automatico alle {REPORT_TIME}")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
