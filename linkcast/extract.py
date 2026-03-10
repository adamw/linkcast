from __future__ import annotations

import logging
from dataclasses import dataclass

import trafilatura

logger = logging.getLogger(__name__)


@dataclass
class Article:
    url: str
    title: str
    text: str
    word_count: int


def extract_article(url: str) -> Article | None:
    """Fetch a URL and extract its article content. Returns None on failure."""
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            logger.warning("Failed to fetch %s", url)
            return None

        text = trafilatura.extract(downloaded)
        if not text:
            logger.warning("No article content extracted from %s", url)
            return None

        metadata = trafilatura.extract(downloaded, output_format="json", include_comments=False)
        import json
        meta = json.loads(metadata) if metadata else {}
        title = meta.get("title", url)

        return Article(
            url=url,
            title=title,
            text=text,
            word_count=len(text.split()),
        )
    except Exception:
        logger.warning("Error extracting %s", url, exc_info=True)
        return None
