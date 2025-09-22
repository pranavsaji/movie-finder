# app.py
from __future__ import annotations
import os
from dotenv import load_dotenv
from ui import build_app

def main():
    """
    Synchronous main function.
    UI elements will be populated by Gradio's 'load' event.
    """
    load_dotenv()
    # The 'genres_choices' are no longer pre-fetched here.
    demo = build_app()

    # Enable the queue for stable async handling
    demo.queue()
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", "7861")),
        show_error=True,
    )

if __name__ == "__main__":
    main()