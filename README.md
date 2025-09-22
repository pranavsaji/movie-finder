# \u2728 Movie Finder (Gradio)

A modern movie discovery app with:
- keyword search
- rich previews (poster, rating, synopsis, trailer)
- \u201cWatch\u201d links gathered from the web
- browse by **genre** and **language**
- pagination and adjustable page size

## Setup

1) Clone & install deps
```bash
git clone https://github.com/yourname/movie-finder.git
cd movie-finder
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure environment

```bash
cp .env.example .env
# Fill TMDB_API_KEY (required)
# Optionally add SERPAPI_API_KEY for broader \u201cwatch\u201d links
```

3. Run

```bash
python app.py
# open http://127.0.0.1:7860
```

## Notes

* **TMDB** powers metadata, posters, and trailers.
* **SerpAPI** (optional) performs Google searches for \u201cwatch\u201d links (e.g., Netflix, Amazon, YouTube, etc.).
* If SerpAPI is missing, we still show IMDB and any movie homepage.

## Customization

* Change default language via `DEFAULT_LANG` in `.env`.
* Force region (for watch providers) via `REGION=US` (ISO-3166-1).
* To use Google CSE instead of SerpAPI, replace `services/search.py` with your CSE call.
