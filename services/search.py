# services/search.py
from __future__ import annotations
import os
from typing import List, Tuple
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

SERP_BASE = "https://serpapi.com/search.json"

def serp_enabled() -> bool:
    return bool(os.getenv("SERPAPI_API_KEY"))

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4))
async def google_watch_links(title: str, year: str | None) -> List[Tuple[str, str]]:
    """
    Return (title, url) list from Google search results for 'watch <title> (<year>) online'.
    """
    if not serp_enabled():
        return []
    
    q = f'watch "{title}" online' + (f" ({year})" if year else "")
    params = {
        "q": q,
        "api_key": os.getenv("SERPAPI_API_KEY"),
        "engine": "google",
        "num": "10",
        "safe": "active"
    }
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(SERP_BASE, params=params)
        r.raise_for_status()
        data = r.json()
    
    out: List[Tuple[str, str]] = []
    # pull organic_results and video results if available
    for item in data.get("organic_results", [])[:10]:
        link = item.get("link")
        title_txt = item.get("title")
        if link and title_txt:
            out.append((title_txt, link))
    
    for vr in data.get("video_results", [])[:5]:
        link = vr.get("link")
        title_txt = vr.get("title")
        if link and title_txt:
            out.append((title_txt + " (Video)", link))
    
    # Deduplicate by URL
    seen = set()
    unique = []
    for t, u in out:
        if u not in seen:
            unique.append((t, u))
            seen.add(u)
    return unique