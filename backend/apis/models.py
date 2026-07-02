"""
Shared data models used by both pipelines (api_based.py and web_search_based.py)
"""

import re
from dataclasses import dataclass, field
from typing import Literal, Optional

_ISO8601_DURATION_RE = re.compile(
    r"^PT(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?$"
)
_DURATION_MINUTES_RE = re.compile(r"^(\d+)\s*(?:min(?:ute)?s?|m)$")
_DURATION_SECONDS_RE = re.compile(r"^(\d+)\s*(?:s|sec|secs|second|seconds)$")
_DURATION_COMPOUND_RE = re.compile(
    r"^(?:(?P<hours>\d+)\s*h(?:ours?)?)?"
    r"\s*(?:(?P<minutes>\d+)\s*m(?:in(?:ute)?s?)?)?"
    r"\s*(?:(?P<seconds>\d+)\s*s(?:ec(?:ond)?s?)?)?$"
)


def parse_iso8601_duration(iso: str) -> int | None:
    """Parse YouTube-style ISO 8601 durations (e.g. PT1H2M30S) to seconds."""
    match = _ISO8601_DURATION_RE.match(iso.strip())
    if not match:
        return None
    total = (
        int(match.group("hours") or 0) * 3600
        + int(match.group("minutes") or 0) * 60
        + int(match.group("seconds") or 0)
    )
    return total if total > 0 else None


def normalize_duration_seconds(value: int | float | None) -> int | None:
    """Normalize to whole seconds (truncate, do not round up)."""
    if value is None:
        return None
    seconds = int(float(value))
    return seconds if seconds > 0 else None


def seconds_from_millis(ms: int | float | None) -> int | None:
    """Convert millisecond timestamps to whole seconds (floor, never rounds up)."""
    if ms is None:
        return None
    seconds = int(float(ms) // 1000)
    return seconds if seconds > 0 else None


def parse_duration_to_seconds(value: str | int | float | None) -> int | None:
    """Parse seconds, H:MM:SS, mm:ss, '45 min', '754s', or '1h 2m 30s'."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return normalize_duration_seconds(value)

    text = str(value).strip().lower()
    if not text:
        return None
    if text.isdigit():
        return int(text)

    if ":" in text:
        try:
            parts = [int(part.strip()) for part in text.split(":")]
        except ValueError:
            return None
        if len(parts) == 2:
            # MM:SS — always treat as minutes then seconds (e.g. 10:09 -> 609s)
            return parts[0] * 60 + parts[1]
        if len(parts) == 3:
            # H:MM:SS
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        return None

    match = _DURATION_SECONDS_RE.match(text)
    if match:
        return int(match.group(1))

    match = _DURATION_MINUTES_RE.match(text)
    if match:
        return int(match.group(1)) * 60

    match = _DURATION_COMPOUND_RE.match(text)
    if match and any(match.group(name) for name in ("hours", "minutes", "seconds")):
        total = (
            int(match.group("hours") or 0) * 3600
            + int(match.group("minutes") or 0) * 60
            + int(match.group("seconds") or 0)
        )
        return total if total > 0 else None
    return None


def format_duration(seconds: int | None) -> str:
    """Format as H:MM:SS with seconds always shown."""
    if seconds is None or seconds <= 0:
        return "unknown"
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}"


def duration_meta(seconds: int | float | None) -> dict:
    normalized = normalize_duration_seconds(seconds)
    return {
        "duration_seconds": normalized,
        "duration_display": format_duration(normalized),
    }


def resource_length_display(resource: "Resource") -> str | None:
    """Human-readable length for video/podcast resources, or None for other types."""
    if resource.type not in ("video", "podcast"):
        return None
    seconds = resource.meta.get("duration_seconds")
    if isinstance(seconds, (int, float)) and seconds > 0:
        return format_duration(normalize_duration_seconds(seconds))
    return resource.meta.get("duration_display") or "unknown"

ResourceType = Literal["video", "book", "article", "podcast"]


@dataclass
class Resource:
    type: ResourceType
    title: str
    url: str
    source: str                     # e.g. "youtube_api", "google_books_api", "web_search"
    meta: dict = field(default_factory=dict)
    is_valid: Optional[bool] = None
    validation_reason: Optional[str] = None


@dataclass
class FetchResult:
    strategy: str                   # "api_based" or "web_search"
    topic: str
    resources: list[Resource]
    request_count: int              # number of outbound HTTP/API calls made for this topic
    elapsed_seconds: float
    errors: list[str] = field(default_factory=list)
