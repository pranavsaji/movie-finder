# ui.py
from __future__ import annotations
import os
from typing import Any, Dict, List, Tuple
import gradio as gr
from services import tmdb, search
from utils import movie_card_markdown

# --- Environment and Global Configuration ---
DEFAULT_LANG = os.getenv("DEFAULT_LANG", "en")
REGION = os.getenv("REGION", "US")

LANG_CHOICES = [
    ("English", "en"), ("Spanish", "es"), ("French", "fr"), ("German", "de"),
    ("Hindi", "hi"), ("Japanese", "ja"), ("Korean", "ko"), ("Chinese (ZH)", "zh"),
    ("Malayalam", "ml"), ("Tamil", "ta"), ("Telugu", "te"),
]

# Module-level state for genre mapping to be populated on load
_genre_name_to_id: Dict[str, int] = {}

# --- Data Fetching and Processing Logic ---
async def init_genres(lang: str) -> List[Tuple[str, int]]:
    items = await tmdb.get_genres(lang)
    return sorted([(g["name"], g["id"]) for g in items], key=lambda x: x[0].lower())

def render_results(items: List[Dict[str, Any]]) -> str:
    html_parts = ['<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:18px">']
    for m in items:
        # The 'color' style has been removed from here. Styling is now handled by 'movie_card_markdown'.
        card = ['<div style="border:1px solid #e5e7eb;border-radius:14px;padding:14px;background:#fff">']
        card.append(movie_card_markdown(m))
        if m.get("youtube_key"):
            card.append(
                f"""
                <div style="margin-top:10px;border-radius:12px;overflow:hidden">
                  <iframe width="100%" height="180" src="https://www.youtube.com/embed/{m['youtube_key']}"
                    title="YouTube trailer" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
                </div>
                """
            )
        if m.get("links"):
            card.append('<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:10px">')
            for name, url in m["links"][:6]:
                card.append(f'<a href="{url}" target="_blank" style="text-decoration:none;background:#111827;color:#fff;padding:8px 10px;border-radius:10px;font-size:13px">{name}</a>')
            card.append("</div>")
        card.append("</div>")
        html_parts.append("".join(card))
    html_parts.append("</div>")
    return "".join(html_parts)

async def _decorate(movie: Dict[str, Any]) -> Dict[str, Any]:
    d = await tmdb.details(movie["id"], lang=DEFAULT_LANG)
    ykey = tmdb.extract_trailer_youtube_key(d)
    imdb = tmdb.imdb_url(d)
    home = tmdb.homepage(d)
    provs = tmdb.providers(d, REGION)

    links = await search.google_watch_links(movie.get("title") or "", (movie.get("release_date") or "")[:4])
    result_links: List[Tuple[str, str]] = []
    if imdb: result_links.append(("IMDB", imdb))
    if home: result_links.append(("Official Site", home))
    result_links.extend(links)

    seen = set()
    dedup = [t for t in result_links if not (t[1] in seen or seen.add(t[1]))]

    return {
        "id": movie["id"], "title": movie.get("title"), "overview": movie.get("overview"),
        "release_date": movie.get("release_date"), "vote_average": movie.get("vote_average"),
        "poster_url": tmdb.poster_url(movie.get("poster_path"), "w342"),
        "backdrop_url": tmdb.backdrop_url(movie.get("backdrop_path"), "w780"),
        "youtube_key": ykey, "links": dedup, "providers": provs
    }

async def do_search(query: str, lang: str, page: int, page_size: int):
    if not query or not query.strip():
        return "Please enter a search query.", [], 0, 0
    data = await tmdb.search_movies(query.strip(), lang=lang, page=page)
    total = data.get("total_results", 0)
    total_pages = data.get("total_pages", 1)
    batch = data.get("results", [])[:page_size]
    enriched = [await _decorate(m) for m in batch]
    return f"Found {total} result(s).", enriched, total_pages, total

async def do_discover(genre_ids: List[int], lang: str, page: int, page_size: int):
    data = await tmdb.discover_by_genres(genre_ids or [], lang=lang, page=page, region=REGION)
    total = data.get("total_results", 0)
    total_pages = data.get("total_pages", 1)
    batch = data.get("results", [])[:page_size]
    enriched = [await _decorate(m) for m in batch]
    return f"Showing top {len(enriched)} of {total}+", enriched, total_pages, total

# --- Top-Level Async Event Handlers ---
async def populate_genres_on_load(lang: str):
    global _genre_name_to_id
    genres_choices = await init_genres(lang)
    _genre_name_to_id = {name: gid for name, gid in genres_choices}
    return gr.CheckboxGroup(choices=[name for name, _ in genres_choices], label="Select genre(s)")

async def on_search(q, l, p, ps):
    msg, enriched, tp, tr = await do_search(q, l, int(p), int(ps))
    return msg, render_results(enriched), tp, tr, q, enriched

async def go_prev(q, l, p, ps):
    p = max(1, int(p) - 1)
    msg, enriched, tp, tr = await do_search(q, l, p, int(ps))
    return p, msg, render_results(enriched), tp, tr, enriched

async def go_next(q, l, p, ps, tp):
    p = min(int(tp), int(p) + 1) if int(tp) > 0 else int(p) + 1
    msg, enriched, ntp, tr = await do_search(q, l, p, int(ps))
    return p, msg, render_results(enriched), ntp, tr, enriched

async def on_discover(gnames, l, p, ps):
    g_ids = [_genre_name_to_id.get(n) for n in (gnames or []) if _genre_name_to_id.get(n) is not None]
    msg, enriched, tp, tr = await do_discover(g_ids, l, int(p), int(ps))
    return msg, render_results(enriched), tp, tr, gnames

async def go_prev2(gnames, l, p, ps):
    p = max(1, int(p) - 1)
    g_ids = [_genre_name_to_id.get(n) for n in (gnames or []) if _genre_name_to_id.get(n) is not None]
    msg, enriched, tp, tr = await do_discover(g_ids, l, p, int(ps))
    return p, msg, render_results(enriched), tp, tr

async def go_next2(gnames, l, p, ps, tp):
    p = min(int(tp), int(p) + 1) if int(tp) > 0 else int(p) + 1
    g_ids = [_genre_name_to_id.get(n) for n in (gnames or []) if _genre_name_to_id.get(n) is not None]
    msg, enriched, ntp, tr = await do_discover(g_ids, l, p, int(ps))
    return p, msg, render_results(enriched), ntp, tr

# --- UI Construction ---
def build_app():
    with gr.Blocks(theme=gr.themes.Soft(), css=".gradio-container { max-width: 1200px !important; }") as demo:
        gr.Markdown("# 🎬 Movie Finder — Search, Preview & Watch")
        with gr.Tabs():
            with gr.Tab("🔎 Search"):
                with gr.Row():
                    query = gr.Textbox(label="Search movies", placeholder="e.g., Interstellar, Marvel, space adventure…")
                with gr.Row():
                    lang = gr.Dropdown(LANG_CHOICES, value=DEFAULT_LANG, label="Metadata Language")
                    page_size = gr.Slider(label="Results per page", minimum=5, maximum=40, value=12, step=1)
                    page = gr.Number(label="Page", value=1, precision=0)
                    search_btn = gr.Button("Search", variant="primary")
                stats = gr.Markdown("")
                gallery = gr.HTML()
                with gr.Row(visible=True) as nav:
                    prev_btn = gr.Button("◀ Prev")
                    next_btn = gr.Button("Next ▶")
                hidden_total_pages = gr.State(0)
                hidden_total_results = gr.State(0)
                hidden_last_query = gr.State("")
                hidden_last_list = gr.State([])
            with gr.Tab("🎭 Browse by Genre"):
                with gr.Row():
                    genres = gr.CheckboxGroup(choices=[], label="Select genre(s)")
                    lang2 = gr.Dropdown(LANG_CHOICES, value=DEFAULT_LANG, label="Metadata Language")
                with gr.Row():
                    page_size2 = gr.Slider(label="Results per page", minimum=5, maximum=40, value=12, step=1)
                    page2 = gr.Number(label="Page", value=1, precision=0)
                    discover_btn = gr.Button("Show Movies", variant="primary")
                stats2 = gr.Markdown("")
                gallery2 = gr.HTML()
                with gr.Row(visible=True) as nav2:
                    prev_btn2 = gr.Button("◀ Prev")
                    next_btn2 = gr.Button("Next ▶")
                hidden_total_pages2 = gr.State(0)
                hidden_total_results2 = gr.State(0)
                hidden_last_genres = gr.State([])

        # Wiring: Search tab
        search_btn.click(on_search, inputs=[query, lang, page, page_size], outputs=[stats, gallery, hidden_total_pages, hidden_total_results, hidden_last_query, hidden_last_list])
        prev_btn.click(go_prev, [hidden_last_query, lang, page, page_size], [page, stats, gallery, hidden_total_pages, hidden_total_results, hidden_last_list])
        next_btn.click(go_next, [hidden_last_query, lang, page, page_size, hidden_total_pages], [page, stats, gallery, hidden_total_pages, hidden_total_results, hidden_last_list])

        # Wiring: Discover tab
        discover_btn.click(on_discover, [genres, lang2, page2, page_size2], [stats2, gallery2, hidden_total_pages2, hidden_total_results2, hidden_last_genres])
        prev_btn2.click(go_prev2, [hidden_last_genres, lang2, page2, page_size2], [page2, stats2, gallery2, hidden_total_pages2, hidden_total_results2])
        next_btn2.click(go_next2, [hidden_last_genres, lang2, page2, page_size2, hidden_total_pages2], [page2, stats2, gallery2, hidden_total_pages2, hidden_total_results2])
        
        # Lifecycle event to populate genres on startup
        demo.load(populate_genres_on_load, inputs=[lang2], outputs=[genres])

    return demo