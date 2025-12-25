import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import List

from config import DB_PATH, FRESHNESS_DAYS
from db import NewsDB
from notifier import send_digest, send_alert
from sources import collect_all, NewsItem


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("typefeed-parser")


def export_json(items: List[NewsItem], path: Path):
    payload = [item.as_dict() for item in items]
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    logger.info("Фид сохранен: %s (%s записей)", path, len(items))


async def collect(db: NewsDB, out_json: Path | None):
    logger.info("Сбор новостей...")
    items = await collect_all()
    fresh: List[NewsItem] = []
    for item in items:
        if db.exists_hash(item.hash):
            continue
        fresh.append(item)
    inserted = db.add_news([i.as_dict() for i in fresh])
    logger.info("Добавлено %s новых записей (из %s собранных)", inserted, len(items))
    if out_json:
        export_json(fresh, out_json)
    return fresh


async def notify(db: NewsDB, days: int):
    logger.info("Подготовка дайджеста Telegram...")
    recent = db.recent_news(days=days)
    if not recent:
        logger.info("Нет свежих записей для уведомления.")
        return
    await send_digest(recent)


def parse_args():
    parser = argparse.ArgumentParser(description="Сборщик новостей Typefeed")
    parser.add_argument("--collect", action="store_true", help="Собрать новости")
    parser.add_argument("--notify", action="store_true", help="Отправить дайджест в Telegram")
    parser.add_argument("--json", type=Path, default=None, help="Путь для сохранения JSON фида")
    parser.add_argument("--days", type=int, default=FRESHNESS_DAYS, help="Окно дней для уведомления")
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.collect and not args.notify:
        logger.info("Нечего делать. Используйте --collect и/или --notify.")
        return
    db = NewsDB(DB_PATH)
    FAIL_FILE = Path(".fail_count")

    async def runner():
        if args.collect:
            await collect(db, args.json)
        if args.notify:
            await notify(db, args.days)

    async def safe_run():
        try:
            await runner()
            if FAIL_FILE.exists():
                FAIL_FILE.unlink()
            return True
        except Exception as exc:  # noqa: BLE001
            logger.exception("Ошибка выполнения: %s", exc)
            fails = 1
            if FAIL_FILE.exists():
                try:
                    fails = int(FAIL_FILE.read_text().strip() or "0") + 1
                except Exception:
                    fails = 1
            FAIL_FILE.write_text(str(fails))
            if fails >= 3:
                await send_alert(f"Парсер упал {fails} раз подряд. Ошибка: {exc}")
            return False

    asyncio.run(safe_run())


if __name__ == "__main__":
    main()

