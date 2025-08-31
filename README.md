
# Quotex Signal Bot (Railway-ready)

Features
- 1-minute signal flow with 3 messages (pair → signal → result)
- Schedule: 09:00–04:00 Asia/Dhaka
- Works in personal chat or fixed CHAT_ID (for auto scheduler)
- Real + OTC markets list (extendable)

## Deploy (Railway)
1) Push this folder to a GitHub repo.
2) On Railway: New Project → Deploy from GitHub.
3) In Railway project → Variables, set:
   - BOT_TOKEN = your Telegram bot token
   - CHAT_ID   = target chat/group id (needed for auto signals)
4) Deploy. Check logs for "Bot started".

## Local run
```
pip install -r requirements.txt
export BOT_TOKEN=...; export CHAT_ID=...
python main.py
```

## Commands
- /start → shows date + list of pairs, reply with a pair (e.g., `BTC/USDT`) to get the 3-message sequence.

## Note
- Bold+Underline first line is sent as the exact literal text you requested:
  **__Quotex Signal by A.A.M Trader__**
  (No markdown parsing to keep it exactly as written.)
