from datetime import date
from tempfile import NamedTemporaryFile

import httpx
from pypdf import PdfReader

from app.config.settings import get_settings
from app.models.schemas import SourceDocument


settings = get_settings()


async def parse_public_pdf(url: str) -> list[SourceDocument]:
    async with httpx.AsyncClient(
        timeout=settings.request_timeout_seconds,
        follow_redirects=True,
        verify=settings.request_verify_ssl,
    ) as client:
        response = await client.get(url)
        response.raise_for_status()

    with NamedTemporaryFile(suffix=".pdf") as temp_file:
        temp_file.write(response.content)
        temp_file.flush()

        reader = PdfReader(temp_file.name)
        texts: list[str] = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                texts.append(page_text.strip())

    content = "\n".join(texts)
    if not content:
        return []

    return [
        SourceDocument(
            source=url,
            type="pitch_deck_pdf",
            content=content,
            metadata={"date": str(date.today()), "category": "pdf"},
        )
    ]
