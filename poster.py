import streamlit as st
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Create key and urls
API_KEY = st.secrets["TMDB_API_KEY"]
BASE_URL = "https://api.themoviedb.org/3"
POSTER_URL = "https://image.tmdb.org/t/p/w500"

# Configure optimized request session

# Create a persistent session (Reuses connection for speed)
session = requests.Session()

# Configure automatic retry strategy for network glitches/rate limits
retry_strategy = Retry(
    total=5, # Retry up to 5 times before giving up
    backoff_factor=1, # Wait times between retries: 1s, 2s, 4s, 8s, 16s
    status_forcelist=[429, 500, 502, 503, 504], # Retry on rate limits or server errors
    allowed_methods=['GET'] # Only retry safe GET requests
)

# Create an adapter with our retry rules
adapter = HTTPAdapter(max_retries=retry_strategy)

# Mount the adapter to both HTTP and HTTPS protocols
session.mount("http://", adapter)
session.mount("https://", adapter)

# Set a custom user-agent header
session.headers.update({
    "User-Agent":"MovieRecommendationSystem/1.0"
})

# Fetch movie poster function

@st.cache_data(ttl=86400)
def get_movie_poster(movie_title):
    try:
        url = f"{BASE_URL}/search/movie"
        params = {
            "api_key": API_KEY,
            "query": movie_title
        }

        response = session.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        if not results:
            return None

        clean_title = movie_title.strip().lower()

        selected = (
            next((m for m in results if m.get("original_title", "").strip().lower()==clean_title), None) or
            next((m for m in results if m.get("title", "").strip().lower()==clean_title), None) or
            sorted(results, key=lambda x: x.get('release_date', "9999-12-31"))[0]
        )

        poster_path = selected.get('poster_path', None)
        return f"{POSTER_URL}{poster_path}"

    except requests.exceptions.RequestException as e:
        print("TMDB Poster Fetch Error: ", e)
        return None

if __name__ == "__main__":
    poster = get_movie_poster("Avatar")
    print("Poster URL:", poster)