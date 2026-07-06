import os
import sys

# Configure sys.path to include project root for absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))

if project_root not in sys.path:
    sys.path.append(project_root)

import asyncio
import httpx
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

def clean_search_query(query: str) -> str:
    import re
    # Strip quotes
    q = query.strip().strip("'\"")
    
    # Match and remove leading verbs, articles, and resource types
    leading_pattern = re.compile(
        r'^(?:listen\s+to|watch|read|find|search\s+for|get|use|learn\s+from|study)\s+'
        r'(?:a|an|the|some|our|your|my|recommended)?\s*'
        r'(?:podcast|video|book|article|audio|show|episode|clip|resource|reading|material)?\s*'
        r'(?:on|about|for|of|to|regarding)?\s*',
        re.IGNORECASE
    )
    q = leading_pattern.sub('', q)
    
    # Also handle if it just starts with "podcast on...", "video about..."
    leading_noun_pattern = re.compile(
        r'^(?:podcast|video|book|article|audio|show|episode|clip|resource|reading|material)\s+'
        r'(?:on|about|for|of|to|regarding)\s*',
        re.IGNORECASE
    )
    q = leading_noun_pattern.sub('', q)
    
    # Remove trailing resource type keywords
    trailing_pattern = re.compile(
        r'\s+(?:podcast|video|book|article|audio|show|episode|clip|resource|reading|material)$',
        re.IGNORECASE
    )
    # Only remove trailing if it doesn't make the query empty
    cleaned = trailing_pattern.sub('', q)
    if cleaned.strip():
        q = cleaned
        
    return q.strip().strip("'\".,;:-\b") if q.strip() else query

async def fetch_and_validate_resources(query: str, allowed_types: list[str], max_duration_seconds: int | None = None, client: httpx.AsyncClient | None = None) -> list[dict]:
    # If no resource types are allowed, return empty list immediately
    if not allowed_types:
        return []

    cleaned_query = clean_search_query(query)

    fetcher = ApiBasedFetcher(client=client)
    validator = LinkValidator(client=client)
    
    search_tasks = []
    types_mapped = []

    # Map search functions
    if "video" in allowed_types:
        search_tasks.append(fetcher.search_youtube(cleaned_query, max_results=2))
        types_mapped.append("video")
    if "audio" in allowed_types:
        search_tasks.append(fetcher.search_podcasts(cleaned_query, max_results=2))
        types_mapped.append("audio")
    if "book" in allowed_types:
        search_tasks.append(fetcher.search_books(cleaned_query, max_results=2))
        types_mapped.append("book")
    if "article" in allowed_types:
        search_tasks.append(fetcher.search_articles(cleaned_query, max_results=2))
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


def ensure_fallback_resources(t: dict, allowed_types: list[str] = None) -> dict:
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

    cleaned_title = clean_search_query(t.get('title', ''))

    if requires_video and "video" not in fetched_types:
        if allowed_types is None or "video" in allowed_types:
            q_title = cleaned_title or 'Instructional Video'
            resources.append({
                "type": "video",
                "resource_type": "video",
                "title": f"Recommended video: {q_title}",
                "url": f"https://www.youtube.com/results?search_query={urllib.parse.quote(q_title)}",
                "reason": f"A helpful video resource to guide you through: {t.get('title', '')}.",
                "is_valid": True,
                "duration": duration_display,
                "duration_display": duration_display,
            })
            fetched_types.add("video")

    if requires_audio and not any(x in fetched_types for x in ("audio", "podcast")):
        if allowed_types is None or "audio" in allowed_types:
            q_title = cleaned_title or 'Podcast Episode'
            resources.append({
                "type": "audio",
                "resource_type": "audio",
                "title": f"Recommended audio: {q_title}",
                "url": f"https://podcasts.apple.com/us/search?term={urllib.parse.quote(q_title)}",
                "reason": f"A helpful audio episode to listen to: {t.get('title', '')}.",
                "is_valid": True,
                "duration": duration_display,
                "duration_display": duration_display,
            })
            fetched_types.add("audio")

    if wants_reading and not any(x in fetched_types for x in ("book", "article")):
        res_type = "book" if "book" in text or "chapter" in text else "article"
        if allowed_types is None or res_type in allowed_types:
            q_title = cleaned_title or 'Reading Material'
            fallback_url = (
                f"https://books.google.com/books?q={urllib.parse.quote(q_title)}"
                if res_type == "book"
                else f"https://www.google.com/search?q={urllib.parse.quote(q_title)}"
            )
            resources.append({
                "type": res_type,
                "resource_type": res_type,
                "title": f"Recommended {res_type}: {q_title}",
                "url": fallback_url,
                "reason": f"A helpful {res_type} to read: {t.get('title', '')}.",
                "is_valid": True,
                "duration": duration_display,
                "duration_display": duration_display,
            })
            fetched_types.add(res_type)

    return t

