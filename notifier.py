import asyncio
import logging
from textwrap import shorten
from typing import List, Dict, Any

from telegram import Bot
from telegram.constants import ParseMode

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


logger = logging.getLogger(__name__)


def _get_bot():
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("Telegram token not configured; skipping send.")
        return None
    return Bot(token=TELEGRAM_BOT_TOKEN)


def _build_message(items: List[Dict[str, Any]]) -> str:
    lines = ["🔥 Typefeed — свежие релизы и типографика", ""]
    for item in items:
        title = item.get("title", "")
        url = item.get("url", "")
        tags = item.get("tags", "")
        snippet = shorten(item.get("content_snippet", ""), width=240, placeholder="…")
        tags_str = f" #{' #'.join(tags.split(','))}" if tags else ""
        lines.append(f"• <b>{title}</b>{tags_str}")
        lines.append(f"{snippet}")
        lines.append(f"{url}")
        lines.append("")
    return "\n".join(lines)


async def send_digest(news_items: List[Dict[str, Any]], limit: int = 5):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram token or chat id not configured; skipping notify.")
        return

    bot = _get_bot()
    if not bot:
        return
    top_items = news_items[:limit]
    message = _build_message(top_items)
    if len(message) > 4000:
        message = message[:3900] + "…"

    await bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=message,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=False,
    )
    logger.info("Telegram digest sent (%s items)", len(top_items))


async def send_alert(text: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram token or chat id not configured; skipping alert.")
        return
    bot = _get_bot()
    if not bot:
        return
    await bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=f"⚠️ Typefeed alert:\n{text}",
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
    logger.info("Telegram alert sent")

