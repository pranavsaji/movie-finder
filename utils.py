# utils.py
from __future__ import annotations
from typing import Any, Dict

def safe_num(v: Any, default=0.0) -> float:
    try:
        return float(v) if v is not None else default
    except Exception:
        return default

def movie_card_markdown(m: Dict[str, Any]) -> str:
    # Build a clean markdown string for a movie card in Gradio
    title = m.get("title") or ""
    year = (m.get("release_date") or "")[:4]
    rating = m.get("vote_average") or 0
    overview = m.get("overview") or ""
    poster = m.get("poster_url")
    lines = []
    if poster:
        lines.append(f'<img src="{poster}" alt="{title}" style="max-width:150px;border-radius:12px;box-shadow:0 8px 20px rgba(0,0,0,0.15);" />')
    lines.append(f"<h3 style='margin:6px 0'>{title} ({year})</h3>")
    lines.append(f"<div style='opacity:0.75'>\u2b50 {rating:.1f} / 10</div>")
    if overview:
        lines.append(f"<p style='margin-top:6px'>{overview}</p>")
    return "\n".join(lines)