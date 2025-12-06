import asyncio
from typing import List, Optional, Dict, Any

import httpx


REDDIT_BASE = "https://www.reddit.com"
DEFAULT_HEADERS = {
    # Identifying UA reduces risk of 429 and blocked requests
    "User-Agent": "stealth_app/0.1 (by u/your_username)"
}


def _build_url(subreddit: str, sort: str, time_filter: Optional[str]) -> str:
    path = f"/r/{subreddit}/{sort}.json"
    if sort == "top" and time_filter:
        return f"{REDDIT_BASE}{path}?t={time_filter}"
    return f"{REDDIT_BASE}{path}"


async def fetch_subreddit_posts(
    subreddit: str,
    sort: str = "hot",
    time_filter: Optional[str] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    if not subreddit:
        raise ValueError("subreddit is required")
    if sort not in {"hot", "new", "top", "rising"}:
        raise ValueError("invalid sort")
    if limit < 1 or limit > 100:
        raise ValueError("limit out of bounds (1-100)")

    url = _build_url(subreddit, sort, time_filter)

    async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=15.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()

    children = data.get("data", {}).get("children", [])
    posts: List[Dict[str, Any]] = []
    for child in children[:limit]:
        d = child.get("data", {})
        posts.append(
            {
                "id": d.get("id", ""),
                "title": d.get("title", ""),
                "author": d.get("author"),
                "score": d.get("score", 0),
                "num_comments": d.get("num_comments", 0),
                "created_utc": d.get("created_utc", 0.0),
                "url": d.get("url_overridden_by_dest") or d.get("url"),
                "permalink": d.get("permalink", ""),
                "subreddit": d.get("subreddit", subreddit),
                "thumbnail": d.get("thumbnail") if isinstance(d.get("thumbnail"), str) else None,
            }
        )

    return posts



