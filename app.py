# app.py
from __future__ import annotations
import asyncio, os
from dotenv import load_dotenv
from ui import build_app, init_genres

def main():
    load_dotenv()
    genres_choices = asyncio.run(init_genres(os.getenv("DEFAULT_LANG", "en")))
    demo = build_app(genres_choices)
    port = int(os.getenv("PORT", "7861"))  # pick anything not in use
    demo.queue()
    demo.launch(server_name="0.0.0.0", server_port=port, show_error=True, max_threads=40)

if __name__ == "__main__":
    main()
