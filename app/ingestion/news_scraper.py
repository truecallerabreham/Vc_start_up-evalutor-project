from datetime import date
from urllib.parse import quote_plus
from xml.etree import ElementTree as ET

import httpx

from app.config.settings import get_settings
from app.models.schemas import SourceDocument


settings = get_settings()


async def scrape_news(startup_name: str, max_articles: int = 5) -> list[SourceDocument]:
    if max_articles <= 0:
        return []

    query = quote_plus(f"{startup_name} startup")
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

    async with httpx.AsyncClient(
        timeout=settings.request_timeout_seconds,
        follow_redirects=True,
        verify=settings.request_verify_ssl,
    ) as client:
        response = await client.get(rss_url)
        response.raise_for_status()

    root = ET.fromstring(response.text)
    items = root.findall(".//item")[:max_articles]

    docs: list[SourceDocument] = []
    today = str(date.today())
    for item in items:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        description = (item.findtext("description") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        content = "\n".join(part for part in [title, description] if part)
        if not content:
            continue

        docs.append(
            SourceDocument(
                source=link or "google_news",
                type="news_article",
                content=content,
                metadata={
                    "date": today,
                    "published": pub_date,
                    "category": "news",
                    "startup_name": startup_name,
                },
            )
        )

    return docs
