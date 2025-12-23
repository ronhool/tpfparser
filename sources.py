import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable, List, Dict, Any, Optional
from urllib.parse import urljoin

import aiohttp
import feedparser
from bs4 import BeautifulSoup
from selectolax.parser import HTMLParser

from config import TAG_KEYWORDS, FRESHNESS_DAYS, MIN_WORDS
from db import compute_hash


logger = logging.getLogger(__name__)


@dataclass
class NewsItem:
    title: str
    url: str
    pub_date: Optional[datetime]
    tags: List[str]
    content_snippet: str
    source: str
    hash: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "pub_date": self.pub_date.isoformat() if self.pub_date else None,
            "tags": self.tags,
            "content_snippet": self.content_snippet,
            "hash": self.hash,
            "source": self.source,
        }


@dataclass
class Source:
    name: str
    url: str
    kind: str  # rss or html
    parser: Callable


def word_count(text: str) -> int:
    return len(text.split())


def is_lang_supported(text: str) -> bool:
    # Simple heuristic: allow if text contains mostly Latin/Cyrillic letters.
    latin = sum(ch.isalpha() and "a" <= ch.lower() <= "z" for ch in text)
    cyr = sum("\u0400" <= ch <= "\u04FF" for ch in text)
    total = latin + cyr
    if total == 0:
        return False
    ratio = (latin + cyr) / max(len(text), 1)
    return ratio > 0.2


def matches_tags(text: str) -> List[str]:
    lower = text.lower()
    return [tag for tag in TAG_KEYWORDS if tag in lower]


def build_item(
    title: str,
    link: str,
    desc: str,
    source_name: str,
    default_tag: Optional[str],
    base_url: str,
    pub_dt: Optional[datetime] = None,
) -> Optional[NewsItem]:
    if not title or not link:
        return None
    link_abs = urljoin(base_url, link)
    tags = matches_tags(f"{title} {desc}")
    if not tags and default_tag:
        tags = [default_tag]
    snippet = desc[:1200]
    if not tags:
        return None
    return NewsItem(
        title=title,
        url=link_abs,
        pub_date=pub_dt or datetime.utcnow().replace(tzinfo=timezone.utc),
        tags=tags,
        content_snippet=snippet,
        source=source_name,
        hash=compute_hash(title, link_abs, snippet),
    )


def extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # Prefer main/article sections if available.
    main = soup.find("main") or soup.find("article") or soup.body
    if not main:
        return ""
    # Remove script/style/nav
    for tag in main(["script", "style", "nav", "header", "footer", "noscript"]):
        tag.decompose()
    text = main.get_text(" ", strip=True)
    return " ".join(text.split())


def parse_rss(url: str, source_name: str) -> List[NewsItem]:
    feed = feedparser.parse(url)
    items: List[NewsItem] = []
    for entry in feed.entries:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        summary = BeautifulSoup(entry.get("summary", ""), "html.parser").get_text(" ", strip=True)
        published = entry.get("published_parsed")
        pub_dt = datetime.fromtimestamp(datetime(*published[:6]).timestamp(), tz=timezone.utc) if published else None
        tags = matches_tags(f"{title} {summary}")
        if not tags:
            tags = ["typography"]
        snippet = summary[:1000]
        if not title or not link:
            continue
        items.append(
            NewsItem(
                title=title,
                url=link,
                pub_date=pub_dt,
                tags=tags,
                content_snippet=snippet,
                source=source_name,
                hash=compute_hash(title, link, snippet),
            )
        )
    return items


async def fetch_html(session: aiohttp.ClientSession, url: str, retries: int = 3, backoff: float = 1.5) -> str:
    for attempt in range(retries):
        try:
            ssl_opt = False if "eyeondesign.aiga.org" in url else None
            async with session.get(url, timeout=20, ssl=ssl_opt) as resp:
                if resp.status == 429:
                    await asyncio.sleep(backoff * (attempt + 1))
                    continue
                resp.raise_for_status()
                return await resp.text()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Fetch failed (%s attempt %s): %s", url, attempt + 1, exc)
            await asyncio.sleep(backoff * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {url}")


async def parse_myfonts(session: aiohttp.ClientSession, url: str, source_name: str) -> List[NewsItem]:
    # The endpoint sometimes moves; try a few known paths.
    candidates = [
        url,
        "https://www.myfonts.com/hotnew-fonts",
        "https://www.myfonts.com/pages/whatsnew",
    ]
    html = None
    last_err = None
    for candidate in candidates:
        try:
            html = await fetch_html(session, candidate)
            break
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            continue
    if html is None:
        raise RuntimeError(last_err or f"Failed to fetch {url}")

    tree = HTMLParser(html)
    cards = tree.css("a.HotNewFonts-card") or tree.css("a.Card-link")
    items: List[NewsItem] = []
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    for card in cards[:30]:
        title_node = card.css_first(".HotNewFonts-card-title") or card.css_first(".Card-title")
        if not title_node:
            continue
        title = title_node.text(strip=True)
        link = card.attributes.get("href")
        if link and link.startswith("/"):
            link = f"https://www.myfonts.com{link}"
        snippet_node = card.css_first(".HotNewFonts-card-description") or card.css_first(".Card-description")
        snippet = snippet_node.text(strip=True) if snippet_node else ""
        tags = matches_tags(f"{title} {snippet}") or ["font release"]
        items.append(
            NewsItem(
                title=title,
                url=link or url,
                pub_date=now,
                tags=tags,
                content_snippet=snippet,
                source=source_name,
                hash=compute_hash(title, link or url, snippet),
            )
        )
    return items


async def parse_typewolf(session: aiohttp.ClientSession, url: str, source_name: str) -> List[NewsItem]:
    html = await fetch_html(session, url)
    soup = BeautifulSoup(html, "html.parser")
    resources = soup.select("section.resources .resource")
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    items: List[NewsItem] = []
    for res in resources:
        title_el = res.select_one("h3")
        link_el = res.select_one("a")
        if not title_el or not link_el:
            continue
        title = title_el.get_text(strip=True)
        link = link_el.get("href")
        desc = res.get_text(" ", strip=True)
        tags = matches_tags(desc) or ["typography"]
        items.append(
            NewsItem(
                title=title,
                url=link or url,
                pub_date=now,
                tags=tags,
                content_snippet=desc[:800],
                source=source_name,
                hash=compute_hash(title, link or url, desc),
            )
        )
    return items


async def parse_fontsinuse(session: aiohttp.ClientSession, url: str, source_name: str) -> List[NewsItem]:
    html = await fetch_html(session, url)
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article.card")
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    items: List[NewsItem] = []
    for card in cards[:15]:
        title_el = card.select_one("h2 a")
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        link = title_el.get("href")
        if link and link.startswith("/"):
            link = f"https://fontsinuse.com{link}"
        snippet = card.get_text(" ", strip=True)
        tags = matches_tags(snippet) or ["typefaces"]
        items.append(
            NewsItem(
                title=title,
                url=link or url,
                pub_date=now,
                tags=tags,
                content_snippet=snippet[:900],
                source=source_name,
                hash=compute_hash(title, link or url, snippet),
            )
        )
    return items


async def parse_wallpaper(session: aiohttp.ClientSession, url: str, source_name: str) -> List[NewsItem]:
    html = await fetch_html(session, url)
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article")[:20]
    items: List[NewsItem] = []
    for card in cards:
        title_el = card.find(["h3", "h2"])
        link_el = card.find("a")
        if not title_el or not link_el:
            continue
        title = title_el.get_text(strip=True)
        link = link_el.get("href")
        desc = card.get_text(" ", strip=True)
        item = build_item(title, link, desc, source_name, default_tag=None, base_url=url)
        if item:
            items.append(item)
    return items


async def parse_dezeen(session: aiohttp.ClientSession, url: str, source_name: str) -> List[NewsItem]:
    html = await fetch_html(session, url)
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("li.dezeen-story, article")[:25]
    items: List[NewsItem] = []
    for card in cards:
        link_el = card.find("a")
        title_el = card.find(["h2", "h3"]) or link_el
        if not title_el or not link_el:
            continue
        title = title_el.get_text(strip=True)
        link = link_el.get("href")
        desc = card.get_text(" ", strip=True)
        item = build_item(title, link, desc, source_name, default_tag=None, base_url=url)
        if item:
            items.append(item)
    return items


async def parse_itsnicethat(session: aiohttp.ClientSession, url: str, source_name: str) -> List[NewsItem]:
    html = await fetch_html(session, url)
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article, .card")[:25]
    items: List[NewsItem] = []
    for card in cards:
        title_el = card.find(["h2", "h3"])
        link_el = card.find("a")
        if not title_el or not link_el:
            continue
        title = title_el.get_text(strip=True)
        link = link_el.get("href")
        desc = card.get_text(" ", strip=True)
        item = build_item(title, link, desc, source_name, default_tag=None, base_url=url)
        if item:
            items.append(item)
    return items


async def parse_eyeondesign(session: aiohttp.ClientSession, url: str, source_name: str) -> List[NewsItem]:
    html = await fetch_html(session, url)
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article")[:20]
    items: List[NewsItem] = []
    for card in cards:
        title_el = card.find(["h2", "h3"])
        link_el = card.find("a")
        if not title_el or not link_el:
            continue
        title = title_el.get_text(strip=True)
        link = link_el.get("href")
        desc = card.get_text(" ", strip=True)
        item = build_item(title, link, desc, source_name, default_tag="typography", base_url=url)
        if item:
            items.append(item)
    return items


async def parse_creativereview(session: aiohttp.ClientSession, url: str, source_name: str) -> List[NewsItem]:
    html = await fetch_html(session, url)
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article, .cr-card")[:20]
    items: List[NewsItem] = []
    for card in cards:
        title_el = card.find(["h2", "h3"])
        link_el = card.find("a")
        if not title_el or not link_el:
            continue
        title = title_el.get_text(strip=True)
        link = link_el.get("href")
        desc = card.get_text(" ", strip=True)
        item = build_item(title, link, desc, source_name, default_tag=None, base_url=url)
        if item:
            items.append(item)
    return items


async def parse_designweek(session: aiohttp.ClientSession, url: str, source_name: str) -> List[NewsItem]:
    html = await fetch_html(session, url)
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article")[:20]
    items: List[NewsItem] = []
    for card in cards:
        title_el = card.find(["h2", "h3"])
        link_el = card.find("a")
        if not title_el or not link_el:
            continue
        title = title_el.get_text(strip=True)
        link = link_el.get("href")
        desc = card.get_text(" ", strip=True)
        item = build_item(title, link, desc, source_name, default_tag=None, base_url=url)
        if item:
            items.append(item)
    return items


async def parse_brandidentity(session: aiohttp.ClientSession, url: str, source_name: str) -> List[NewsItem]:
    html = await fetch_html(session, url)
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article, .Card")[:20]
    items: List[NewsItem] = []
    for card in cards:
        title_el = card.find(["h2", "h3"])
        link_el = card.find("a")
        if not title_el or not link_el:
            continue
        title = title_el.get_text(strip=True)
        link = link_el.get("href")
        desc = card.get_text(" ", strip=True)
        item = build_item(title, link, desc, source_name, default_tag="typography", base_url=url)
        if item:
            items.append(item)
    return items


async def parse_printmag_typetuesday(session: aiohttp.ClientSession, url: str, source_name: str) -> List[NewsItem]:
    html = await fetch_html(session, url)
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article")[:20]
    items: List[NewsItem] = []
    for card in cards:
        title_el = card.find(["h2", "h3"])
        link_el = card.find("a")
        if not title_el or not link_el:
            continue
        title = title_el.get_text(strip=True)
        link = link_el.get("href")
        desc = card.get_text(" ", strip=True)
        item = build_item(title, link, desc, source_name, default_tag="typography", base_url=url)
        if item:
            items.append(item)
    return items


async def parse_monotype(session: aiohttp.ClientSession, url: str, source_name: str) -> List[NewsItem]:
    html = await fetch_html(session, url)
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article, .news-card")[:20]
    items: List[NewsItem] = []
    for card in cards:
        title_el = card.find(["h2", "h3"])
        link_el = card.find("a")
        if not title_el or not link_el:
            continue
        title = title_el.get_text(strip=True)
        link = link_el.get("href")
        desc = card.get_text(" ", strip=True)
        item = build_item(title, link, desc, source_name, default_tag="font release", base_url=url)
        if item:
            items.append(item)
    return items


async def parse_typography_dot_com(session: aiohttp.ClientSession, url: str, source_name: str) -> List[NewsItem]:
    html = await fetch_html(session, url)
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article, .post-card")[:20]
    items: List[NewsItem] = []
    for card in cards:
        title_el = card.find(["h2", "h3"])
        link_el = card.find("a")
        if not title_el or not link_el:
            continue
        title = title_el.get_text(strip=True)
        link = link_el.get("href")
        desc = card.get_text(" ", strip=True)
        item = build_item(title, link, desc, source_name, default_tag="typography", base_url=url)
        if item:
            items.append(item)
    return items


async def parse_commercialtype(session: aiohttp.ClientSession, url: str, source_name: str) -> List[NewsItem]:
    html = await fetch_html(session, url)
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article, .news-item")[:20]
    items: List[NewsItem] = []
    for card in cards:
        title_el = card.find(["h2", "h3"])
        link_el = card.find("a")
        if not title_el or not link_el:
            continue
        title = title_el.get_text(strip=True)
        link = link_el.get("href")
        desc = card.get_text(" ", strip=True)
        item = build_item(title, link, desc, source_name, default_tag="font release", base_url=url)
        if item:
            items.append(item)
    return items


async def parse_productiontype(session: aiohttp.ClientSession, url: str, source_name: str) -> List[NewsItem]:
    html = await fetch_html(session, url)
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article, .article")[:20]
    items: List[NewsItem] = []
    for card in cards:
        title_el = card.find(["h2", "h3"])
        link_el = card.find("a")
        if not title_el or not link_el:
            continue
        title = title_el.get_text(strip=True)
        link = link_el.get("href")
        desc = card.get_text(" ", strip=True)
        item = build_item(title, link, desc, source_name, default_tag="font release", base_url=url)
        if item:
            items.append(item)
    return items


async def parse_daltonmaag(session: aiohttp.ClientSession, url: str, source_name: str) -> List[NewsItem]:
    html = await fetch_html(session, url)
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article, .news-card")[:15]
    items: List[NewsItem] = []
    for card in cards:
        title_el = card.find(["h2", "h3"])
        link_el = card.find("a")
        if not title_el or not link_el:
            continue
        title = title_el.get_text(strip=True)
        link = link_el.get("href")
        desc = card.get_text(" ", strip=True)
        item = build_item(title, link, desc, source_name, default_tag="font release", base_url=url)
        if item:
            items.append(item)
    return items


async def parse_fontfabric(session: aiohttp.ClientSession, url: str, source_name: str) -> List[NewsItem]:
    html = await fetch_html(session, url)
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article, .blog-item")[:15]
    items: List[NewsItem] = []
    for card in cards:
        title_el = card.find(["h2", "h3"])
        link_el = card.find("a")
        if not title_el or not link_el:
            continue
        title = title_el.get_text(strip=True)
        link = link_el.get("href")
        desc = card.get_text(" ", strip=True)
        item = build_item(title, link, desc, source_name, default_tag="font release", base_url=url)
        if item:
            items.append(item)
    return items


async def parse_typetogether(session: aiohttp.ClientSession, url: str, source_name: str) -> List[NewsItem]:
    html = await fetch_html(session, url)
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article, .news-item")[:20]
    items: List[NewsItem] = []
    for card in cards:
        title_el = card.find(["h2", "h3"])
        link_el = card.find("a")
        if not title_el or not link_el:
            continue
        title = title_el.get_text(strip=True)
        link = link_el.get("href")
        desc = card.get_text(" ", strip=True)
        item = build_item(title, link, desc, source_name, default_tag="font release", base_url=url)
        if item:
            items.append(item)
    return items


SOURCES: List[Source] = [
    Source("Typecache", "https://typecache.com/news/rss", "rss", parse_rss),
    Source("FreeTypography", "https://freetypography.com/feed", "rss", parse_rss),
    Source("TypographyDaily", "https://feeds.feedburner.com/TypographyDaily", "rss", parse_rss),
    Source("TypewolfResources", "https://www.typewolf.com/resources", "html", parse_typewolf),
    Source("FontsInUse", "https://fontsinuse.com", "html", parse_fontsinuse),
    Source("Wallpaper", "https://www.wallpaper.com/", "html", parse_wallpaper),
    Source("Dezeen", "https://www.dezeen.com/", "html", parse_dezeen),
    Source("ItsNiceThat", "https://www.itsnicethat.com", "html", parse_itsnicethat),
    Source("AIGAEyeOnDesign", "https://eyeondesign.aiga.org", "html", parse_eyeondesign),
    Source("CreativeReview", "https://www.creativereview.co.uk", "html", parse_creativereview),
    Source("DesignWeek", "https://www.designweek.co.uk", "html", parse_designweek),
    Source("TheBrandIdentity", "https://the-brandidentity.com", "html", parse_brandidentity),
    Source("PrintMagTypeTuesday", "https://www.printmag.com/type-tuesday", "html", parse_printmag_typetuesday),
    Source("MonotypeNews", "https://www.monotype.com/company/news-press", "html", parse_monotype),
    Source("TypographyComBranding", "https://typography.com/blog/tag/Branding", "html", parse_typography_dot_com),
    Source("CommercialType", "https://commercialtype.com", "html", parse_commercialtype),
    Source("ProductionType", "https://productiontype.com", "html", parse_productiontype),
    Source("DaltonMaag", "https://www.daltonmaag.com", "html", parse_daltonmaag),
    Source("Fontfabric", "https://www.fontfabric.com", "html", parse_fontfabric),
    Source("TypeTogether", "https://www.type-together.com", "html", parse_typetogether),
]


async def enrich_items_content(items: List[NewsItem], session: aiohttp.ClientSession, concurrency: int = 5) -> List[NewsItem]:
    sem = asyncio.Semaphore(concurrency)

    async def enrich(item: NewsItem) -> NewsItem:
        if word_count(item.content_snippet) >= MIN_WORDS:
            return item
        if not item.url or not item.url.startswith("http"):
            return item
        try:
            async with sem:
                html = await fetch_html(session, item.url, retries=2, backoff=1.2)
            text = extract_text_from_html(html)
            if word_count(text) >= MIN_WORDS:
                snippet = text[:1200]
                item.content_snippet = snippet
                item.hash = compute_hash(item.title, item.url, snippet)
        except Exception as exc:  # noqa: BLE001
            logger.debug("Enrich failed for %s: %s", item.url, exc)
        return item

    return await asyncio.gather(*(enrich(i) for i in items))


async def collect_all() -> List[NewsItem]:
    cutoff = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(days=FRESHNESS_DAYS)
    items: List[NewsItem] = []
    async with aiohttp.ClientSession(headers={"User-Agent": "typefeed-parser/1.0"}) as session:
        tasks = []
        for src in SOURCES:
            if src.kind == "rss":
                tasks.append(asyncio.to_thread(src.parser, src.url, src.name))
            else:
                tasks.append(src.parser(session, src.url, src.name))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for src, result in zip(SOURCES, results):
            if isinstance(result, Exception):
                logger.error("Failed to fetch %s: %s", src.name, result)
                continue
            for item in result:
                # Date filter
                if item.pub_date and item.pub_date < cutoff:
                    continue
                # Tags filter
                if not item.tags:
                    continue
                items.append(item)
        # Enrich short items by fetching full page content, then apply filters.
        items = await enrich_items_content(items, session)
        filtered: List[NewsItem] = []
        for item in items:
            if word_count(item.content_snippet) < MIN_WORDS:
                continue
            if not is_lang_supported(item.content_snippet):
                continue
            filtered.append(item)
        items = filtered
    return items

