# Typefeed Parser

Async news collector for the Telegram channel **@typefeed**. Gathers 3–5 relevant type/typography news per day from curated RSS and HTML sources, deduplicates, stores in SQLite, exports JSON, and sends Telegram digests.

## Stack
- Python 3.11+
- `aiohttp`, `feedparser`, `beautifulsoup4`, `selectolax`
- SQLite (built-in)
- `python-telegram-bot`

## Structure
```
typefeed-parser/
├── parser.py        # CLI entrypoint
├── sources.py       # source list + parsers (RSS/HTML)
├── db.py            # SQLite CRUD + hashing
├── notifier.py      # Telegram digest sender
├── config.py        # tokens, tags, thresholds
├── requirements.txt
└── cron.sh          # daily cron helper
```

## Setup
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Set env vars (не храните токены в git):
```
export TYPEFEED_TELEGRAM_BOT_TOKEN=xxx
export TYPEFEED_TELEGRAM_CHAT_ID=123456
# optional: TYPEFEED_FRESHNESS_DAYS=14
```

## Run
- Collect only: `python parser.py --collect --json feed.json`
- Notify only: `python parser.py --notify --days 2`
- Both: `python parser.py --collect --notify --json feed.json`

## Scheduling (cron 08:00 MSK)
```
0 5 * * * TZ=Europe/Moscow /bin/bash -c '/path/to/typefeed-parser/cron.sh >> /var/log/typefeed.log 2>&1'
```

## Notes
- Filters: last 14 days (override via `TYPEFEED_FRESHNESS_DAYS`), word count ≥200, English/Russian (langid fallback), tag match from `TAG_KEYWORDS` in `config.py`.
- Alerts: при 3 подряд ошибках отправляется предупреждение в Telegram (тот же чат). `.fail_count` хранит счетчик.
- Секреты: токен/чат должны приходить из окружения; `cron.sh` использует env, а не хардкод.
- Dedup by SHA256 hash (title+url+snippet).
- Extend tags (examples): `variable fonts`, `open source font`, `foundry`, `display fonts`, `serif`, `sans serif`, `mono`, `color font`.
- Adjust freshness or minimum words via environment variables in `config.py`.

