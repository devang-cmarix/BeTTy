"""
Validates resource URLs concurrently after either pipeline produces them.
"""

import asyncio
import re
from urllib.parse import quote

import httpx

from .models import Resource

YOUTUBE_RE = re.compile(r"(?:youtu\.be/|youtube\.com/watch\?v=|youtube\.com/shorts/)([\w-]{6,})")


class LinkValidator:
    def __init__(self, concurrency: int = 8, timeout: float = 8.0, client: httpx.AsyncClient | None = None):
        self.semaphore = asyncio.Semaphore(concurrency)
        self.timeout = timeout
        self.client = client or httpx.AsyncClient(
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"},
            timeout=httpx.Timeout(timeout, connect=min(timeout, 5.0)),
            follow_redirects=True,
        )
        self._owns_client = (client is None)

    async def close(self):
        if self._owns_client:
            await self.client.aclose()

    async def validate(self, resource: Resource) -> Resource:
        async with self.semaphore:
            try:
                if self._youtube_id(resource.url):
                    ok, reason = await asyncio.wait_for(
                        self._check_youtube(resource.url),
                        timeout=self.timeout,
                    )
                else:
                    ok, reason = await asyncio.wait_for(
                        self._check_generic(resource.url),
                        timeout=self.timeout,
                    )
            except Exception as e:
                ok, reason = False, f"error:{type(e).__name__}"
        resource.is_valid = ok
        resource.validation_reason = reason
        return resource

    async def validate_all(self, resources: list[Resource]) -> list[Resource]:
        if not resources:
            return []
        return list(await asyncio.gather(*(self.validate(r) for r in resources)))

    @staticmethod
    def _youtube_id(url: str) -> str | None:
        m = YOUTUBE_RE.search(url)
        return m.group(1) if m else None

    async def _check_youtube(self, url: str) -> tuple[bool, str]:
        oembed = f"https://www.youtube.com/oembed?url={quote(url, safe='')}&format=json"
        resp = await self.client.get(oembed)
        return (resp.status_code == 200), f"oembed_{resp.status_code}"

    async def _check_generic(self, url: str) -> tuple[bool, str]:
        try:
            resp = await self.client.head(url)
            if resp.status_code == 405 or resp.status_code >= 400:
                resp = await self.client.get(url)   # some CMS/article hosts 405 on HEAD
            return (resp.status_code < 400), f"http_{resp.status_code}"
        except Exception as e:
            return False, f"error:{type(e).__name__}"
