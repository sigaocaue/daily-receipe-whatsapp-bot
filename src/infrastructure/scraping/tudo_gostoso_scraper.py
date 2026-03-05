import logging

import httpx

from config import settings

logger = logging.getLogger(__name__)

SCRAPER_TIMEOUT = 30.0


class TudoGostosoScraper:
    async def scrape(self, url: str | None = None) -> dict:
        params = {"url": url} if url else {}
        async with httpx.AsyncClient(timeout=SCRAPER_TIMEOUT) as client:
            response = await client.get(settings.TUDO_GOSTOSO_SCRAPER_URL, params=params)
            response.raise_for_status()
            return response.json()
