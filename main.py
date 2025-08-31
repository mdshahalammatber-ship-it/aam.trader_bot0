
import os
import asyncio
from datetime import datetime, time
import pytz

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ---------- CONFIG ----------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")  # required for auto signals
TIMEZONE = pytz.timezone("Asia/Dhaka")  # your requested TZ
# Add/extend all Quotex markets as needed
MARKETS = [
    "BTC/USDT", "ETH/USDT",
    "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD",
    "XAU/USD", "XAG/USD"
]
# ---------------------------

def now_bd():
    return datetime.now(TIMEZONE)

def fmt_date():
    return now_bd().strftime("%Y-%m-%d")

def fmt_hm():
    # 24-hour format HH:MM
    return now_bd().strftime("%H:%M")

# ---- Simple demo signal generator (placeholder for your strategies) ----
# You can plug in EMA/RSI/MACD/BB logic here later.
def generate_signal(pair: str):
    import random
    signal = random.choice(["Call", "Put"])
    emoji = "🟢" if signal == "Call" else "🔴"
    duration = "1m"
    entry_time = fmt_hm()  # 24h
    # Optional: MTG recovery step suggestion (1-3)
    mtg_step = random.choice([1, 2, 3])
    return signal, emoji, duration, entry_time, mtg_step

def generate_result():
    import random
    res = random.choice(["Win", "Loss"])
    emo = "✅" if res == "Win" else "❌"
    return res, emo

# ---------------- Telegram Handlers ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    header = "**__Quotex Signal by A.A.M Trader__**"
    msg = f"{header}\nDate: {fmt_date()}\n" \
          f"Select Pair (reply with one):\n" + "\n".join(MARKETS)
    await update.message.reply_text(msg)

async def handle_pair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if text not in MARKETS:
        await update.message.reply_text("❌ Invalid pair.\nReply with one of:\n" + "\n".join(MARKETS))
        return

    pair = text

    # 1st message (pair info)
    msg1 = f"**__Quotex Signal by A.A.M Trader__**\n" \
           f"Date: {fmt_date()}\n" \
           f"Pair: {pair}"
    await update.message.reply_text(msg1)

    # 2nd message (signal)
    signal, s_emoji, duration, entry_time, mtg = generate_signal(pair)
    msg2 = f"**__Quotex Signal by A.A.M Trader__**\n" \
           f"Pair: {pair}\n" \
           f"Signal: {signal} {s_emoji}\n" \
           f"Duration: {duration}\n" \
           f"Entry Time: {entry_time}\n" \
           f"MTG Step: {mtg}"
    await update.message.reply_text(msg2)

    # wait 60s (1-minute trade), then send result
    await asyncio.sleep(60)
    result, r_emoji = generate_result()
    msg3 = f"**__Quotex Signal by A.A.M Trader__**\n" \
           f"Pair: {pair}\n" \
           f"Result: {result} {r_emoji}"
    await update.message.reply_text(msg3)

# --------------- Scheduler (09:00 → 04:00) -----------------
def within_schedule(dt: datetime) -> bool:
    # Active between 09:00 and 04:00 next day (Asia/Dhaka)
    start_t = time(9, 0)   # 09:00
    end_t   = time(4, 0)   # 04:00
    t = dt.time()
    return (t >= start_t) or (t <= end_t)

async def auto_signal_task(app):
    # Sends 2nd + 3rd messages automatically to CHAT_ID for every pair
    if not CHAT_ID:
        return  # skip if not configured
    if not within_schedule(now_bd()):
        return

    for pair in MARKETS:
        signal, s_emoji, duration, entry_time, mtg = generate_signal(pair)
        msg2 = f"**__Quotex Signal by A.A.M Trader__**\n" \
               f"Pair: {pair}\n" \
               f"Signal: {signal} {s_emoji}\n" \
               f"Duration: {duration}\n" \
               f"Entry Time: {entry_time}\n" \
               f"MTG Step: {mtg}"
        await app.bot.send_message(chat_id=CHAT_ID, text=msg2)

        await asyncio.sleep(60)  # 1-minute trade window

        result, r_emoji = generate_result()
        msg3 = f"**__Quotex Signal by A.A.M Trader__**\n" \
               f"Pair: {pair}\n" \
               f"Result: {result} {r_emoji}"
        await app.bot.send_message(chat_id=CHAT_ID, text=msg3)

async def post_init(app):
    # Run auto_signal_task every minute
    async def tick(context):
        await auto_signal_task(app)

    app.job_queue.run_repeating(tick, interval=60, first=5)  # start after 5s, then every 60s

def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN missing. Set env var BOT_TOKEN.")
        return
    # CHAT_ID is optional for manual use, required for auto scheduler
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_pair))

    # set up job queue after app starts
    application.post_init = post_init

    print("✅ Bot starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
