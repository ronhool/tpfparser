import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import List

from config import DB_PATH, FRESHNESS_DAYS
from db import NewsDB
from notifier import send_digest
from sources import collect_all, NewsItem


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("typefeed-parser")


def export_json(items: List[NewsItem], path: Path):
    payload = [item.as_dict() for item in items]
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    logger.info("Saved feed: %s (%s items)", path, len(items))


async def collect(db: NewsDB, out_json: Path | None):
    logger.info("Collecting news...")
    items = await collect_all()
    fresh: List[NewsItem] = []
    for item in items:
        if db.exists_hash(item.hash):
            continue
        fresh.append(item)
    inserted = db.add_news([i.as_dict() for i in fresh])
    logger.info("Inserted %s new items (from %s collected)", inserted, len(items))
    if out_json:
        export_json(fresh, out_json)
    return fresh


async def notify(db: NewsDB, days: int):
    logger.info("Preparing Telegram digest...")
    recent = db.recent_news(days=days)
    if not recent:
        logger.info("No recent items to notify.")
        return
    await send_digest(recent)


def parse_args():
    parser = argparse.ArgumentParser(description="Typefeed news collector")
    parser.add_argument("--collect", action="store_true", help="Collect news")
    parser.add_argument("--notify", action="store_true", help="Send Telegram digest")
    parser.add_argument("--json", type=Path, default=None, help="Path to save JSON feed")
    parser.add_argument("--days", type=int, default=FRESHNESS_DAYS, help="Days window for notification")
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.collect and not args.notify:
        logger.info("Nothing to do. Use --collect and/or --notify.")
        return
    db = NewsDB(DB_PATH)

    async def runner():
        if args.collect:
            await collect(db, args.json)
        if args.notify:
            await notify(db, args.days)

    asyncio.run(runner())


if __name__ == "__main__":
    main()

