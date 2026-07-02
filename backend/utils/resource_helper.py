import os
import sys

# Configure sys.path to include project root for absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))

if project_root not in sys.path:
    sys.path.append(project_root)

import asyncio
from backend.apis.api_based import ApiBasedFetcher
from backend.apis.validator import LinkValidator
from backend.apis.models import (
    Resource as ApiResource,
    resource_length_display,
    parse_duration_to_seconds,
)

def get_allowed_resource_types(learning_preferences):
    allowed = []
    for preference in learning_preferences:
        normalized = preference.lower()
        if "reading" in normalized:
            allowed.append("book")
            allowed.append("article")
        if "video" in normalized or "watching" in normalized:
            allowed.append("video")
        if "audio" in normalized or "podcast" in normalized or "listening" in normalized:
            allowed.append("audio")
    return list(dict.fromkeys(allowed))

async def fetch_and_validate_resources(query: str, allowed_types: list[str], max_duration_seconds: int | None = None) -> list[dict]:
    # If no resource types are allowed, return empty list immediately
    if not allowed_types:
        return []

    fetcher = ApiBasedFetcher()
    validator = LinkValidator()
    
    search_tasks = []
    types_mapped = []

    # Map search functions
    if "video" in allowed_types:
        search_tasks.append(fetcher.search_youtube(query, max_results=2))
        types_mapped.append("video")
    if "audio" in allowed_types:
        search_tasks.append(fetcher.search_podcasts(query, max_results=2))
        types_mapped.append("audio")
    if "book" in allowed_types:
        search_tasks.append(fetcher.search_books(query, max_results=2))
        types_mapped.append("book")
    if "article" in allowed_types:
        search_tasks.append(fetcher.search_articles(query, max_results=2))
        types_mapped.append("article")

    if not search_tasks:
        await fetcher.close()
        await validator.close()
        return []

    # Concurrently search resources
    search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
    
    all_resources = []
    for res_list in search_results:
        if isinstance(res_list, list):
            all_resources.extend(res_list)

    if not all_resources:
        await fetcher.close()
        await validator.close()
        return []


    # Concurrently validate links
    validated_resources = await validator.validate_all(all_resources)

    # Attempt to enrich YouTube durations for video resources if possible
    try:
        await fetcher._enrich_youtube_durations([r for r in validated_resources if getattr(r, 'type', None) == 'video'])
    except Exception:
        # Non-fatal; continue even if enrichment fails
        pass

    # Clean up fetcher and validator connections
    await fetcher.close()
    await validator.close()

    # Optionally filter by max duration (seconds) for video/podcast items
    if max_duration_seconds is not None:
        filtered_validated = []
        for r in validated_resources:
            # If resource has duration metadata, exclude if longer than allowed
            # Try to parse any duration_display strings into seconds if needed
            if r.type in ("video", "podcast") and not isinstance(r.meta.get("duration_seconds"), (int, float)):
                dd = r.meta.get("duration_display") or r.meta.get("duration")
                parsed = parse_duration_to_seconds(dd) if dd else None
                if parsed:
                    r.meta["duration_seconds"] = parsed

            dur = r.meta.get("duration_seconds")
            if r.type in ("video", "podcast") and isinstance(dur, (int, float)):
                if dur > max_duration_seconds:
                    continue
            filtered_validated.append(r)
        validated_resources = filtered_validated

    formatted_resources = []
    for r in validated_resources:
        if not getattr(r, "url", None):
            continue

        # Extract duration
        duration = resource_length_display(r)

        # Build a helpful reason/context
        reason = ""
        if r.type == "video":
            channel = r.meta.get("channel", "")
            reason = f"Watch this video by {channel}." if channel else "Watch this instructional video."
        elif r.type == "podcast":
            podcast_name = r.meta.get("podcast", "")
            artist = r.meta.get("artist", "")
            if podcast_name and artist:
                reason = f"Listen to {podcast_name} by {artist}."
            elif podcast_name:
                reason = f"Listen to this episode from {podcast_name}."
            else:
                reason = "Listen to this podcast episode."
        elif r.type == "book":
            authors = r.meta.get("authors", [])
            author_str = ", ".join(authors) if isinstance(authors, list) else str(authors)
            reason = f"Recommended reading by {author_str}." if author_str else "Recommended book."
        elif r.type == "article":
            snippet = r.meta.get("snippet", "")
            reason = snippet if snippet else "Read this informative article."

        formatted_resources.append({
            "type": r.type,  # Frontend expected type key
            "resource_type": r.type,  # Alternative schema key
            "title": r.title,
            "url": r.url,
            "reason": reason,
            "is_valid": getattr(r, "is_valid", None),
            "duration": duration,
            "duration_display": duration, # Backup key for duration
        })

    return formatted_resources


def update_task_with_real_resources(t: dict) -> dict:
    resources = t.get("resources", [])
    if not resources:
        return t

    primary_res = resources[0]
    res_type = primary_res.get("type", "") or primary_res.get("resource_type", "")
    res_title = primary_res.get("title", "")
    
    t_title = t.get("title", "")
    t_desc = t.get("description", "")

    display_title = res_title
    if len(display_title) > 60:
        display_title = display_title[:57] + "..."

    import re
    if res_type == "video":
        verb = "Watch"
        noun = "video"
    elif res_type in ("audio", "podcast"):
        verb = "Listen to"
        noun = "podcast"
    elif res_type in ("book", "article"):
        verb = "Read"
        noun = "book" if res_type == "book" else "article"
    else:
        verb = "Use"
        noun = "resource"

    # Replace phrases like "Find a podcast", "Search for a video", etc.
    pattern = re.compile(
        r'(?i)\b(find|search\s+for|look\s+up|choose|select|pick|identify|source)\s+(?:an?|the)?\s*([a-z-]+\s+)?(podcast|video|book|article|short|episode|clip)\b'
    )
    
    if pattern.search(t_desc):
        t_desc = pattern.sub(f"{verb} the recommended {noun} '{display_title}'", t_desc)
    else:
        t_desc = f"{verb} the recommended {noun} '{display_title}': {t_desc}"

    title_pattern = re.compile(r'(?i)\b(find|search\s+for|listen\s+to|watch|read)\s+(?:an?|the)?\s*([a-z-]+\s+)?(podcast|video|book|article|short|episode|clip)\b')
    if title_pattern.match(t_title):
        t_title = f"{verb} '{display_title}'"
    else:
        t_title = f"{t_title}: '{display_title}'"

    t["title"] = t_title
    t["description"] = t_desc
    return t


def ensure_fallback_resources(t: dict) -> dict:
    text = " ".join([
        str(t.get("title", "")),
        str(t.get("description", "")),
        str(t.get("rationale", "")),
    ]).lower()

    requires_audio = any(w in text for w in ("listen", "hear", "podcast", "audio"))
    requires_video = any(w in text for w in ("watch", "watching", "video", "youtube"))
    wants_reading = any(w in text for w in ("read", "book", "article", "chapter"))

    if not (requires_audio or requires_video or wants_reading):
        return t

    resources = t.setdefault("resources", [])
    fetched_types = {r.get("type", "").lower() for r in resources}

    import urllib.parse
    duration_mins = t.get("duration_minutes", 15)
    duration_display = f"{duration_mins} min"

    if requires_video and "video" not in fetched_types:
        resources.append({
            "type": "video",
            "resource_type": "video",
            "title": f"Recommended video: {t.get('title', 'Instructional Video')}",
            "url": f"https://www.youtube.com/results?search_query={urllib.parse.quote(t.get('title', 'Instructional Video'))}",
            "reason": f"A helpful video resource to guide you through: {t.get('title', '')}.",
            "is_valid": True,
            "duration": duration_display,
            "duration_display": duration_display,
        })
        fetched_types.add("video")

    if requires_audio and not any(x in fetched_types for x in ("audio", "podcast")):
        resources.append({
            "type": "audio",
            "resource_type": "audio",
            "title": f"Recommended audio: {t.get('title', 'Podcast Episode')}",
            "url": f"https://www.google.com/search?q={urllib.parse.quote(t.get('title', 'Podcast Episode'))}+podcast",
            "reason": f"A helpful audio episode to listen to: {t.get('title', '')}.",
            "is_valid": True,
            "duration": duration_display,
            "duration_display": duration_display,
        })
        fetched_types.add("audio")

    if wants_reading and not any(x in fetched_types for x in ("book", "article")):
        res_type = "book" if "book" in text or "chapter" in text else "article"
        resources.append({
            "type": res_type,
            "resource_type": res_type,
            "title": f"Recommended {res_type}: {t.get('title', 'Reading Material')}",
            "url": f"https://www.google.com/search?q={urllib.parse.quote(t.get('title', 'Reading Material'))}+{res_type}",
            "reason": f"A helpful {res_type} to read: {t.get('title', '')}.",
            "is_valid": True,
            "duration": duration_display,
            "duration_display": duration_display,
        })
        fetched_types.add(res_type)

    return t

