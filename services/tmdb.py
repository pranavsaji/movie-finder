# services/tmdb.py
from __future__ import annotations
import os
from typing import Any, Dict, List, Optional, Tuple
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

TMDB_BASE = "https://api.themoviedb.org/3"
IMG_BASE = "https://image.tmdb.org/t/p"

def _headers() -> Dict[str, str]:
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        raise RuntimeError("TMDB_API_KEY missing")
    return {"Authorization": f"Bearer {api_key}"} if api_key.startswith("eyJ") else {}

def _params(extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    p = {"api_key": os.getenv("TMDB_API_KEY")}
    if extra:
        p.update(extra)
    return p

def poster_url(path: Optional[str], size: str = "w342") -> Optional[str]:
    if not path:
        return None
    return f"{IMG_BASE}/{size}{path}"

def backdrop_url(path: Optional[str], size: str = "w780") -> Optional[str]:
    if not path:
        return None
    return f"{IMG_BASE}/{size}{path}"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4))
async def _get(client: httpx.AsyncClient, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    r = await client.get(f"{TMDB_BASE}{endpoint}", params=params, headers=_headers(), timeout=20)
    r.raise_for_status()
    return r.json()

async def get_genres(lang: str = "en") -> List[Dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        data = await _get(client, "/genre/movie/list", _params({"language": lang}))
        return data.get("genres", [])

async def search_movies(query: str, lang: str = "en", page: int = 1) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        data = await _get(client, "/search/movie", _params({"query": query, "language": lang, "page": page, "include_adult": False}))
        return data

# --- MODIFIED: Added 'original_language' parameter ---
async def discover_by_genres(
    genre_ids: List[int], 
    lang: str = "en", 
    page: int = 1, 
    region: Optional[str]=None,
    original_language: Optional[str]=None
) -> Dict[str, Any]:
    params = {
        "with_genres": ",".join(map(str, genre_ids)) if genre_ids else None,
        "language": lang,
        "page": page,
        "sort_by": "popularity.desc",
        "include_adult": False
    }
    if region:
        params["region"] = region
        params["watch_region"] = region
    # --- NEW: Add the original language filter if provided ---
    if original_language:
        params["with_original_language"] = original_language
        
    # remove None
    params = {k: v for k, v in params.items() if v is not None}
    async with httpx.AsyncClient() as client:
        return await _get(client, "/discover/movie", _params(params))

async def details(movie_id: int, lang: str = "en") -> Dict[str, Any]:
    append = "videos,external_ids,watch/providers"
    async with httpx.AsyncClient() as client:
        return await _get(client, f"/movie/{movie_id}", _params({"language": lang, "append_to_response": append}))

def extract_trailer_youtube_key(movie: Dict[str, Any]) -> Optional[str]:
    vids = (movie.get("videos") or {}).get("results") or []
    # Prefer official trailer
    for v in vids:
        if v.get("site") == "YouTube" and v.get("type") == "Trailer":
            return v.get("key")
    # fallback any YouTube video
    for v in vids:
        if v.get("site") == "YouTube":
            return v.get("key")
    return None

def imdb_url(movie: Dict[str, Any]) -> Optional[str]:
    external = movie.get("external_ids") or {}
    imdb_id = external.get("imdb_id")
    return f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else None

def homepage(movie: Dict[str, Any]) -> Optional[str]:
    return movie.get("homepage") or None

def providers(movie: Dict[str, Any], region: Optional[str]) -> List[Tuple[str, str]]:
    out = []
    prov = (movie.get("watch/providers") or {}).get("results") or {}
    if region and region in prov:
        region_data = prov[region]
        for bucket in ["flatrate", "buy", "rent", "ads", "free"]:
            for p in region_data.get(bucket, []):
                out.append((p.get("provider_name", bucket), f"https://www.themoviedb.org/provider/{p.get('provider_id')}"))
    return out