import logging

import httpx


logger = logging.getLogger(__name__)


class UnsplashImageFetcherMixin:
    _unsplash_key: str

    async def fetch_image_url(self, query: str) -> str | None:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.unsplash.com/search/photos",
                    params={"query": query, "per_page": 1, "orientation": "landscape"},
                    headers={"Authorization": f"Client-ID {self._unsplash_key}"},
                )
                response.raise_for_status()
                data = response.json()
                if data["results"]:
                    return data["results"][0]["urls"]["regular"]
        except Exception as e:
            logger.warning("Failed to fetch image from Unsplash: %s", e)
        return None
