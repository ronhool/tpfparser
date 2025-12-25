import os
from datetime import timezone, timedelta

# Default configuration values. Override via environment variables in production.
TELEGRAM_BOT_TOKEN = os.getenv("TYPEFEED_TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TYPEFEED_TELEGRAM_CHAT_ID", "")

# Tags that define relevant content for the channel.
TAG_KEYWORDS = [
    "typefaces",
    "typography",
    "fonts",
    "font release",
    "type design",
    "variable fonts",
    "display fonts",
    "serif",
    "sans serif",
    "mono",
    "script",
    "color font",
    "open source font",
    "foundry",
    # Additional typography terms
    "lettering",
    "calligraphy",
    "hand lettering",
    "font family",
    "typeface design",
    "font design",
    "type specimen",
    "font pairing",
    "kerning",
    "tracking",
    "leading",
    "ligature",
    "opentype",
    "webfont",
    "web font",
    "font licensing",
    "font foundry",
    "type foundry",
    "branding typography",
    "editorial typography",
    "book typography",
    "magazine typography",
    "poster typography",
    "logo typography",
    "custom type",
    "bespoke font",
    "custom font",
    "retro font",
    "vintage font",
    "modern font",
    "geometric font",
    "humanist font",
    "transitional font",
    "old style font",
    "blackletter",
    "gothic font",
    "decorative font",
    "handwriting font",
    "brush font",
    "stencil font",
    "grunge font",
    "cyrillic font",
    "multilingual font",
    "arabic font",
    "chinese font",
    "japanese font",
    "font update",
    "font upgrade",
    "font sale",
    "free font",
    "premium font",
    "commercial font",
]

# SQLite file name.
DB_PATH = os.getenv("TYPEFEED_DB_PATH", "news.db")

# Collect items from the last N days only (default 14 days).
FRESHNESS_DAYS = int(os.getenv("TYPEFEED_FRESHNESS_DAYS", "14"))

# Minimal word count to keep an article.
MIN_WORDS = int(os.getenv("TYPEFEED_MIN_WORDS", "200"))

# Timezone for scheduling/formatting (Moscow default).
MSK = timezone(timedelta(hours=3))

