import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Collection Names (Bronze, Silver, Gold Architecture)
COLLECTION_BRONZE_YOUTUBE = "bronze_youtube"
COLLECTION_BRONZE_NEWS = "bronze_news"
COLLECTION_SILVER_COMMENTS = "silver_comments"
COLLECTION_SILVER_NEWS = "silver_news"
COLLECTION_GOLD_SENTIMENT = "gold_sentiment"

# YouTube Data API Settings
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "").strip()
DEFAULT_SEARCH_QUERIES = [
    "putusan mk ijazah gibran",
    "gibran ijazah palsu sidang mk",
    "gugatan ijazah gibran mahkamah konstitusi"
]
MAX_VIDEOS_TO_FETCH = int(os.getenv("MAX_VIDEOS_TO_FETCH", "5"))
MAX_COMMENTS_PER_VIDEO = int(os.getenv("MAX_COMMENTS_PER_VIDEO", "100"))

# News Scraper Settings
NEWS_SEARCH_QUERY = os.getenv("NEWS_SEARCH_QUERY", "putusan mk ijazah gibran")
SCRAPLING_HEADLESS = os.getenv("SCRAPLING_HEADLESS", "True").lower() in ("true", "1", "yes")

# Data & Model Paths
DATA_DIR = BASE_DIR / "data"
SLANG_DICT_PATH = DATA_DIR / "slang_dictionary.json"
STOPWORDS_PATH = DATA_DIR / "stopwords_id.txt"
TRAINING_SEED_PATH = DATA_DIR / "training_seed.json"
MODEL_SAVE_PATH = DATA_DIR / "model_sentiment.pkl"

DB_NAME = os.getenv("DB_NAME", "bigdata_sentiment_mk")

_cached_resolved_uri = None

def get_wsl_ip() -> str:
    """Mengambil alamat IP distro WSL default jika berjalan di Windows."""
    try:
        res = subprocess.run(
            ["wsl", "-d", "Ubuntu", "hostname", "-I"],
            capture_output=True,
            text=True,
            timeout=3
        )
        if res.returncode == 0:
            ips = res.stdout.strip().split()
            if ips:
                return ips[0]
    except Exception:
        pass
    return None

def resolve_mongo_uri() -> str:
    """
    Menemukan URI MongoDB yang aktif.
    Mendukung Docker network (mongodb://mongodb:27017), .env URI, WSL IP, dan localhost.
    """
    global _cached_resolved_uri
    if _cached_resolved_uri:
        return _cached_resolved_uri

    candidates = []

    # 1. Cek jika hostname internal Docker 'mongodb' dapat di-resolve (berjalan di container)
    try:
        import socket
        socket.gethostbyname("mongodb")
        candidates.append("mongodb://mongodb:27017")
    except Exception:
        pass

    # 2. Cek URI dari environment variable / .env
    env_uri = os.getenv("MONGO_URI", "").strip()
    if env_uri and env_uri not in candidates:
        candidates.append(env_uri)

    # 3. Cek localhost / 127.0.0.1
    for local_uri in ["mongodb://localhost:27017", "mongodb://127.0.0.1:27017"]:
        if local_uri not in candidates:
            candidates.append(local_uri)

    # 4. Cek WSL IP jika di Windows
    wsl_ip = get_wsl_ip()
    if wsl_ip:
        wsl_uri = f"mongodb://{wsl_ip}:27017"
        if wsl_uri not in candidates:
            candidates.append(wsl_uri)

    # Test koneksi ke setiap kandidat
    for uri in candidates:
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=2000)
            client.admin.command("ping")
            _cached_resolved_uri = uri
            return _cached_resolved_uri
        except Exception:
            continue

    # Fallback default
    fallback = candidates[0] if candidates else "mongodb://localhost:27017"
    _cached_resolved_uri = fallback
    return _cached_resolved_uri

MONGO_URI = resolve_mongo_uri()

def get_mongo_client(uri: str = None, timeout_ms: int = 5000) -> MongoClient:
    """Mengembalikan MongoClient dengan URI yang tervalidasi."""
    target_uri = uri or resolve_mongo_uri()
    return MongoClient(target_uri, serverSelectionTimeoutMS=timeout_ms)

def get_mongo_db(uri: str = None, db_name: str = DB_NAME):
    """Mengembalikan objek Database MongoDB."""
    client = get_mongo_client(uri)
    return client[db_name]

def check_mongo_connection(uri: str = None) -> bool:
    """Verifikasi koneksi ke MongoDB."""
    try:
        client = get_mongo_client(uri, timeout_ms=4000)
        client.admin.command("ping")
        return True
    except (ConnectionFailure, ServerSelectionTimeoutError, Exception):
        return False
