"""
Podcast search, with 3 interchangeable providers. Switch with:

    export PODCAST_PROVIDER=itunes        # default — no signup, no API key, ever
    export PODCAST_PROVIDER=listennotes   # needs LISTENNOTES_API_KEY
    export PODCAST_PROVIDER=podcastindex  # needs PODCASTINDEX_API_KEY + _SECRET
"""

import asyncio
import hashlib
import os
import time

import httpx

from . import env_loader
from .models import Resource, duration_meta, normalize_duration_seconds, seconds_from_millis
from .rate_limiter import RateLimiter

PODCAST_PROVIDER = os.getenv("PODCAST_PROVIDER", "itunes").lower()

LISTENNOTES_API_KEY = os.getenv("LISTENNOTES_API_KEY")
PODCASTINDEX_API_KEY = os.getenv("PODCASTINDEX_API_KEY")
PODCASTINDEX_API_SECRET = os.getenv("PODCASTINDEX_API_SECRET")

itunes_limiter = RateLimiter(max_calls=1, period=3.0)         # informal ~20 req/min abuse limit
listennotes_limiter = RateLimiter(max_calls=1, period=1.0)    # free tier quota is monthly, not per-sec, but stay polite
podcastindex_limiter = RateLimiter(max_calls=1, period=1.0)   # no published number; conservative default


# ---------------------------------------------------------------------------
# Provider 1: iTunes Search API — no key, no signup, ever
# ---------------------------------------------------------------------------

async def search_itunes(client: httpx.AsyncClient, query: str, max_results: int = 3) -> list[Resource]:
    async with itunes_limiter:
        resp = await client.get(
            "https://itunes.apple.com/search",
            params={
                "term": query,
                "media": "podcast",
                "entity": "podcastEpisode",
                "limit": max_results,
            },
        )
    if resp.status_code != 200:
        return []
    items = resp.json().get("results", [])
    out = []
    for i in items:
        url = i.get("trackViewUrl") or i.get("collectionViewUrl")
        if not url:
            continue
        track_ms = i.get("trackTimeMillis")
        seconds = seconds_from_millis(track_ms)
        meta = {"artist": i.get("artistName"), "podcast": i.get("collectionName")}
        meta.update(duration_meta(seconds))
        out.append(
            Resource(
                type="podcast",
                title=i.get("trackName") or i.get("collectionName", "Unknown episode"),
                url=url,
                source="itunes_api",
                meta=meta,
            )
        )
    return out


# ---------------------------------------------------------------------------
# Provider 2: Listen Notes (PodcastAPI.com)
# ---------------------------------------------------------------------------

def _listennotes_base_url() -> str:
    return "https://listen-api.listennotes.com" if LISTENNOTES_API_KEY else "https://listen-api-test.listennotes.com"


async def search_listennotes(client: httpx.AsyncClient, query: str, max_results: int = 3) -> list[Resource]:
    headers = {"X-ListenAPI-Key": LISTENNOTES_API_KEY} if LISTENNOTES_API_KEY else {}
    async with listennotes_limiter:
        resp = await client.get(
            f"{_listennotes_base_url()}/api/v2/search",
            params={"q": query, "type": "episode", "page_size": max_results},
            headers=headers,
        )
    if resp.status_code != 200:
        return []
    items = resp.json().get("results", [])
    out = []
    for i in items[:max_results]:
        url = i.get("listennotes_url") or i.get("link") or i.get("rss")
        if not url:
            continue
        seconds = normalize_duration_seconds(i.get("audio_length_sec"))
        meta = {"publisher": i.get("publisher_original"), "podcast": i.get("podcast_title_original")}
        meta.update(duration_meta(seconds))
        out.append(
            Resource(
                type="podcast",
                title=i.get("title_original") or i.get("title", "Unknown episode"),
                url=url,
                source="listennotes_api",
                meta=meta,
            )
        )
    return out


# ---------------------------------------------------------------------------
# Provider 3: PodcastIndex
# ---------------------------------------------------------------------------

def _podcastindex_headers() -> dict:
    ts = str(int(time.time()))
    auth_string = f"{PODCASTINDEX_API_KEY}{PODCASTINDEX_API_SECRET}{ts}"
    auth_hash = hashlib.sha1(auth_string.encode("utf-8")).hexdigest()
    return {
        "User-Agent": "fitness-app-resource-fetcher/1.0",
        "X-Auth-Key": PODCASTINDEX_API_KEY or "",
        "X-Auth-Date": ts,
        "Authorization": auth_hash,
    }


async def search_podcastindex(client: httpx.AsyncClient, query: str, max_results: int = 3) -> list[Resource]:
    if not (PODCASTINDEX_API_KEY and PODCASTINDEX_API_SECRET):
        return []
    async with podcastindex_limiter:
        resp = await client.get(
            "https://api.podcastindex.org/api/1.0/episodes/byterm",
            params={"q": query, "max": max_results},
            headers=_podcastindex_headers(),
        )
    if resp.status_code != 200:
        return []
    items = resp.json().get("items", [])
    out = []
    for i in items[:max_results]:
        url = i.get("link") or i.get("enclosureUrl")
        if not url:
            continue
        seconds = normalize_duration_seconds(i.get("duration"))
        meta = {"author": i.get("author"), "podcast": i.get("feedTitle")}
        meta.update(duration_meta(seconds))
        out.append(
            Resource(
                type="podcast",
                title=i.get("title", "Unknown episode"),
                url=url,
                source="podcastindex_api",
                meta=meta,
            )
        )
    return out


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

_PROVIDERS = {
    "itunes": search_itunes,
    "listennotes": search_listennotes,
    "podcastindex": search_podcastindex,
}


async def search_podcasts(client: httpx.AsyncClient, query: str, max_results: int = 3) -> list[Resource]:
    provider = _PROVIDERS.get(PODCAST_PROVIDER, search_itunes)
    return await provider(client, query, max_results)
