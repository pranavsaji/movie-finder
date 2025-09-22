# 🎬 Movie Finder (Gradio)

A modern and intuitive movie discovery web application built with Python and Gradio. Search for any movie, browse by genre, and instantly find where to watch it online.


## ✨ Features

-   **Powerful Search**: Find movies by keyword, title, or actors.
-   **Rich Previews**: Get instant access to movie posters, ratings, a full synopsis, and an embedded YouTube trailer.
-   **"Where to Watch" Links**: Gathers direct links from TMDb providers and Google search results (e.g., Netflix, Prime Video, YouTube) to help you find where a movie is streaming or available for rent/purchase.
-   **Browse by Genre**: Discover new movies by selecting one or multiple genres.
-   **Multi-Language Support**: Choose your preferred language for movie metadata (titles and descriptions).
-   **Interactive UI**: Features clean pagination and an adjustable number of results per page for a smooth browsing experience.

## 🛠️ Technology Stack

This project is powered by several fantastic technologies and services:

-   **Backend**: Python
-   **Web UI**: [Gradio](https.gradio.app)
-   **Movie Data**: [The Movie Database (TMDb) API](https://www.themoviedb.org/documentation/api) for all metadata, posters, trailers, and official watch providers.
-   **Watch Links (Optional)**: [SerpAPI](https://serpapi.com/) for performing Google searches to find a wider range of streaming links.
-   **HTTP Client**: [httpx](https://www.python-httpx.org/) for making robust, asynchronous API calls.
-   **Dependencies**: `gradio`, `httpx`, `python-dotenv`, `pydantic`, `tenacity`.

## 🚀 Getting Started

Follow these steps to set up and run the project on your local machine.

### 1. Prerequisites

-   Python 3.8 or newer.
-   A free API key from [The Movie Database (TMDb)](https://www.themoviedb.org/signup).

### 2. Clone the Repository

Open your terminal and clone the project:

```bash
git clone https://github.com/your-username/movie-finder.git
cd movie-finder
```

### 3. Set Up a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

```bash
# Create the virtual environment
python -m venv .venv

# Activate it (macOS/Linux)
source .venv/bin/activate

# Or activate it (Windows)
# .venv\Scripts\activate
```

### 4. Install Dependencies

Install all the required Python packages using pip:

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

You need to provide your API keys for the application to work.

First, copy the example environment file:

```bash
cp .env.example .env
```

Now, open the newly created `.env` file in a text editor and fill in your keys:

```ini
# Required: Your API key from themoviedb.org
TMDB_API_KEY=your_tmdb_api_key_here

# Optional but recommended for richer “Watch” links
# Get your key from serpapi.com
SERPAPI_API_KEY=your_serpapi_key_here

# Optional: Force a region for TMDb discovery and watch providers (ISO-3166-1 code)
REGION=US

# Optional: Set the default language for metadata (ISO-639-1 code)
DEFAULT_LANG=en
```

-   `TMDB_API_KEY`: **This is mandatory.** The app will not run without it.
-   `SERPAPI_API_KEY`: If you leave this blank, the app will still work, but the "Watch" links will be limited to TMDb's official providers and the movie's homepage.

### 6. Run the Application

You're all set! Start the Gradio web server with this command:

```bash
python app.py
```

Open your web browser and navigate to the local URL shown in your terminal, which is typically `http://127.0.0.1:7861`.

## 📂 Project Structure

Here is an overview of the key files in the project:

```
.
├── app.py              # Main application entry point. Initializes and launches the Gradio app.
├── ui.py               # Defines the Gradio user interface layout, components, and event listeners.
├── utils.py            # Contains helper functions, primarily for generating styled HTML for the UI.
├── services/           # A package for communicating with external APIs.
│   ├── tmdb.py         # Client for The Movie Database (TMDb) API.
│   └── search.py       # Client for the SerpAPI Google Search service.
├── requirements.txt    # A list of all Python dependencies for the project.
├── .env.example        # A template for the required environment variables.
└── README.md           # This file!
```

## 🔧 Customization

You can easily customize the application's default behavior by editing the `.env` file:

-   **Default Language**: Change `DEFAULT_LANG` to any supported [ISO-639-1 language code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) (e.g., `es` for Spanish, `fr` for French) to fetch movie details in that language.
-   **Watch Provider Region**: Change `REGION` to your [ISO-3166-1 country code](https://en.wikipedia.org/wiki/List_of_ISO_3166-1_alpha-2_country_codes) (e.g., `IN` for India, `GB` for Great Britain) to prioritize watch providers available in your country.
-   **Alternative Search Service**: If you prefer not to use SerpAPI, you can modify `services/search.py`. For example, you could replace the `google_watch_links` function with your own implementation using a different service like Google's Custom Search Engine (CSE) API.

## 🤝 Contributing

Contributions are welcome! If you have ideas for new features, find a bug, or want to improve the code, please feel free to open an issue or submit a pull request.

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).