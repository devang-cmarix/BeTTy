"""
Strategy 1: real search APIs, no LLM involved in link generation.
"""

import asyncio
import os
import re
import time
from urllib.parse import quote_plus

import httpx

from . import env_loader
from .models import Resource, FetchResult, duration_meta, parse_iso8601_duration
from .podcast_providers import search_podcasts as _search_podcasts
from .rate_limiter import RateLimiter

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
ARTICLE_SEARCH_PROVIDER = os.getenv("ARTICLE_SEARCH_PROVIDER", "auto").lower()

google_books_limiter = RateLimiter(max_calls=1, period=1.0)
youtube_limiter = RateLimiter(max_calls=5, period=1.0)
serper_limiter = RateLimiter(max_calls=5, period=1.0)

_YOUTUBE_VIDEO_ID_RE = re.compile(
    r"(?:youtu\.be/|youtube\.com/watch\?v=|youtube\.com/shorts/)([\w-]{6,})"
)
_YOUTUBE_VIDEO_URL_RE = re.compile(r"/(?:watch\?v=|shorts/)([\w-]{6,})")
_DURATION_MS_RE = re.compile(r'"approxDurationMs":"(\d+)"')
_DURATION_SECONDS_RE = re.compile(r'"lengthSeconds":"(\d+)"')


def _youtube_video_id(url: str) -> str | None:
    match = _YOUTUBE_VIDEO_ID_RE.search(url)
    return match.group(1) if match else None


class ApiBasedFetcher:
    def __init__(self, client: httpx.AsyncClient | None = None, source_timeout: float = 15.0):
        timeout = httpx.Timeout(10.0, connect=5.0)
        self.client = client or httpx.AsyncClient(timeout=timeout)
        self.source_timeout = source_timeout
        self.request_count = 0
        self._owns_client = (client is None)

    async def close(self):
        if self._owns_client:
            await self.client.aclose()

    async def search_youtube(self, query: str, max_results: int = 3) -> list[Resource]:
        if YOUTUBE_API_KEY:
            try:
                async with youtube_limiter:
                    self.request_count += 1
                    resp = await self.client.get(
                        "https://www.googleapis.com/youtube/v3/search",
                        params={
                            "part": "snippet",
                            "q": query,
                            "type": "video",
                            "maxResults": max_results,
                            "safeSearch": "strict",
                            "key": YOUTUBE_API_KEY,
                        },
                    )
                if resp.status_code == 200:
                    items = resp.json().get("items", [])
                    resources = [
                        Resource(
                            type="video",
                            title=i["snippet"]["title"],
                            url=f"https://www.youtube.com/watch?v={i['id']['videoId']}",
                            source="youtube_api",
                            meta={"channel": i["snippet"]["channelTitle"]},
                        )
                        for i in items
                    ]
                    await self._enrich_youtube_durations(resources)
                    if resources:
                        return resources
            except Exception:
                pass

        # Fallback: use YouTube's public search page when the API path is unavailable.
        try:
            search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
            headers = {"User-Agent": "Mozilla/5.0"}
            async with youtube_limiter:
                self.request_count += 1
                resp = await self.client.get(search_url, headers=headers)
            if resp.status_code != 200:
                return []
            html = resp.text
            seen_ids: set[str] = set()
            resources: list[Resource] = []
            for match in _YOUTUBE_VIDEO_URL_RE.finditer(html):
                video_id = match.group(1)
                if video_id in seen_ids:
                    continue
                seen_ids.add(video_id)
                resources.append(
                    Resource(
                        type="video",
                        title=f"{query} video",
                        url=f"https://www.youtube.com/watch?v={video_id}",
                        source="youtube_fallback",
                        meta={"channel": "YouTube"},
                    )
                )
                if len(resources) >= max_results:
                    break
            if resources:
                await self._enrich_youtube_durations(resources)
            return resources
        except Exception:
            return []

    async def _enrich_youtube_durations(self, resources: list[Resource]) -> None:
        if not resources:
            return

        id_to_resource: dict[str, Resource] = {}
        for resource in resources:
            video_id = _youtube_video_id(resource.url)
            if video_id:
                id_to_resource[video_id] = resource
        if not id_to_resource:
            return

        if YOUTUBE_API_KEY:
            try:
                async with youtube_limiter:
                    self.request_count += 1
                    resp = await self.client.get(
                        "https://www.googleapis.com/youtube/v3/videos",
                        params={
                            "part": "contentDetails",
                            "id": ",".join(id_to_resource),
                            "key": YOUTUBE_API_KEY,
                        },
                    )
                if resp.status_code == 200:
                    for item in resp.json().get("items", []):
                        resource = id_to_resource.get(item.get("id", ""))
                        if resource is None:
                            continue
                        iso_duration = item.get("contentDetails", {}).get("duration", "")
                        resource.meta.update(duration_meta(parse_iso8601_duration(iso_duration)))
                    if any(resource.meta.get("duration_seconds") for resource in resources):
                        return
            except Exception:
                pass

        for resource in resources:
            if resource.meta.get("duration_seconds") or resource.meta.get("duration_display"):
                continue
            video_id = _youtube_video_id(resource.url)
            if not video_id:
                continue
            try:
                watch_url = f"https://www.youtube.com/watch?v={video_id}"
                resp = await self.client.get(watch_url, headers={"User-Agent": "Mozilla/5.0"})
                if resp.status_code != 200:
                    continue
                html = resp.text
                match = _DURATION_MS_RE.search(html) or _DURATION_SECONDS_RE.search(html)
                if not match:
                    continue
                seconds = int(match.group(1)) // 1000 if match.re is _DURATION_MS_RE else int(match.group(1))
                resource.meta.update(duration_meta(seconds))
            except Exception:
                continue

    async def search_books(self, query: str, max_results: int = 3) -> list[Resource]:
        params = {"q": query, "maxResults": max_results}
        if GOOGLE_BOOKS_API_KEY:
            params["key"] = GOOGLE_BOOKS_API_KEY
        async with google_books_limiter:
            self.request_count += 1
            resp = await self.client.get(
                "https://www.googleapis.com/books/v1/volumes", params=params
            )
        if resp.status_code != 200:
            return []
        items = resp.json().get("items", [])
        out = []
        for i in items:
            info = i.get("volumeInfo", {})
            link = info.get("infoLink") or info.get("previewLink")
            if not link:
                continue
            out.append(
                Resource(
                    type="book",
                    title=info.get("title", "Unknown title"),
                    url=link,
                    source="google_books_api",
                    meta={"authors": info.get("authors", [])},
                )
            )
        return out

    async def search_podcasts(self, query: str, max_results: int = 3) -> list[Resource]:
        self.request_count += 1
        return await _search_podcasts(self.client, query, max_results)

    async def fetch_for_topic(self, topic: str) -> FetchResult:
        start = time.monotonic()
        start_count = self.request_count
        errors: list[str] = []
        source_calls = {
            "youtube": self.search_youtube(topic),
            "books": self.search_books(topic),
            "podcasts": self.search_podcasts(topic),
            "articles": self.search_articles(topic),
        }
        results = await asyncio.gather(
            *(asyncio.wait_for(call, timeout=self.source_timeout) for call in source_calls.values()),
            return_exceptions=True,
        )
        resources: list[Resource] = []
        for source, result in zip(source_calls, results):
            if isinstance(result, Exception):
                errors.append(f"{source}: {type(result).__name__}: {result}")
                continue
            resources.extend(result)

        return FetchResult(
            strategy="api_based",
            topic=topic,
            resources=resources,
            request_count=self.request_count - start_count,
            elapsed_seconds=time.monotonic() - start,
            errors=errors,
        )
    
    async def search_articles(self, query: str, max_results: int = 5) -> list[Resource]:
        provider = ARTICLE_SEARCH_PROVIDER
        if provider == "auto":
            provider = "serper" if SERPER_API_KEY else "duckduckgo"

        if provider == "serper":
            return await self.search_articles_serper(query, max_results)
        if provider == "duckduckgo":
            return await self.search_articles_duckduckgo(query, max_results)

        raise RuntimeError(
            "ARTICLE_SEARCH_PROVIDER must be one of: auto, serper, duckduckgo"
        )

    async def search_articles_serper(self, query: str, max_results: int = 5) -> list[Resource]:
        if not SERPER_API_KEY:
            raise RuntimeError(
                "SERPER_API_KEY is not set. Add it to .env or use "
                "ARTICLE_SEARCH_PROVIDER=duckduckgo."
            )

        async with serper_limiter:
            self.request_count += 1
            resp = await self.client.post(
                "https://google.serper.dev/search",
                headers={
                    "X-API-KEY": SERPER_API_KEY,
                    "Content-Type": "application/json",
                },
                json={"q": query, "num": max_results},
            )

        if resp.status_code != 200:
            raise RuntimeError(f"Serper search failed with HTTP {resp.status_code}")

        articles = []
        for item in resp.json().get("organic", [])[:max_results]:
            url = item.get("link")
            if not url:
                continue
            articles.append(
                Resource(
                    type="article",
                    title=item.get("title", ""),
                    url=url,
                    source="serper_api",
                    meta={"snippet": item.get("snippet", "")},
                )
            )
        return articles

    async def search_articles_duckduckgo(self, query: str, max_results: int = 5) -> list[Resource]:
        if DDGS is None:
            raise RuntimeError(
                "DuckDuckGo article search dependency is not installed. "
                "Install ddgs or use ARTICLE_SEARCH_PROVIDER=serper."
            )

        def _search():
            with DDGS() as ddgs:
                return list(
                    ddgs.text(
                        query,
                        max_results=max_results
                    )
                )

        self.request_count += 1
        results = await asyncio.to_thread(_search)

        articles = []
        for item in results:
            url = item.get("href")
            if not url:
                continue
            articles.append(
                Resource(
                    type="article",
                    title=item.get("title", ""),
                    url=url,
                    source="duckduckgo",
                    meta={"snippet": item.get("body", "")}
                )
            )
        return articles
