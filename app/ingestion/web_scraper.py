from datetime import date
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from app.config.settings import get_settings
from app.models.schemas import SourceDocument


settings = get_settings()


async def scrape_website(url: str) -> list[SourceDocument]:
    async with httpx.AsyncClient(
        timeout=settings.request_timeout_seconds,
        follow_redirects=True,
        verify=settings.request_verify_ssl,
    ) as client:
        response = await client.get(url)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    meta_desc = ""
    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    if meta_desc_tag and meta_desc_tag.get("content"):
        meta_desc = meta_desc_tag.get("content").strip()

    headings = "\n".join(h.get_text(" ", strip=True) for h in soup.find_all(["h1", "h2", "h3"]))
    paragraphs = "\n".join(p.get_text(" ", strip=True) for p in soup.find_all("p"))

    domain = urlparse(url).netloc
    today = str(date.today())

    docs: list[SourceDocument] = []
    if title:
        docs.append(
            SourceDocument(
                source=url,
                type="website_title",
                content=title,
                metadata={"date": today, "category": "overview", "domain": domain},
            )
        )
    if meta_desc:
        docs.append(
            SourceDocument(
                source=url,
                type="website_meta_description",
                content=meta_desc,
                metadata={"date": today, "category": "overview", "domain": domain},
            )
        )
    if headings:
        docs.append(
            SourceDocument(
                source=url,
                type="website_headings",
                content=headings,
                metadata={"date": today, "category": "product", "domain": domain},
            )
        )
    if paragraphs:
        docs.append(
            SourceDocument(
                source=url,
                type="website_paragraphs",
                content=paragraphs,
                metadata={"date": today, "category": "details", "domain": domain},
            )
        )

    return docs
