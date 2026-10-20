"""
YouTube Data API v3 Ingestor untuk mengumpulkan video dan komentar publik
terkait putusan MK isu ijazah Gibran.
"""
from datetime import datetime, timezone
import logging
from typing import List, Dict, Any

from config.settings import (
    YOUTUBE_API_KEY,
    DEFAULT_SEARCH_QUERIES,
    MAX_VIDEOS_TO_FETCH,
    MAX_COMMENTS_PER_VIDEO
)
from collectors.mock_data import generate_mock_youtube_data

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def get_youtube_service():
    """Menginisialisasi YouTube API client jika API key tersedia."""
    if not YOUTUBE_API_KEY:
        logger.warning("YOUTUBE_API_KEY tidak ditemukan di .env. Beralih ke fallback sample mode.")
        return None
    try:
        from googleapiclient.discovery import build
        service = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        return service
    except Exception as e:
        logger.error(f"Gagal menginisialisasi YouTube API service: {e}")
        return None

def search_youtube_videos(query: str, max_results: int = MAX_VIDEOS_TO_FETCH) -> List[Dict[str, Any]]:
    """Mencari video relevan di YouTube berdasarkan query."""
    service = get_youtube_service()
    if not service:
        return []

    try:
        logger.info(f"Mencari video YouTube dengan query: '{query}'...")
        request = service.search().list(
            q=query,
            part="snippet",
            type="video",
            maxResults=max_results,
            relevanceLanguage="id"
        )
        response = request.execute()
        videos = []
        for item in response.get("items", []):
            video_id = item["id"].get("videoId")
            snippet = item.get("snippet", {})
            if video_id:
                videos.append({
                    "video_id": video_id,
                    "title": snippet.get("title", ""),
                    "description": snippet.get("description", ""),
                    "channel_title": snippet.get("channelTitle", ""),
                    "published_at": snippet.get("publishedAt", "")
                })
        logger.info(f"Ditemukan {len(videos)} video dari YouTube API.")
        return videos
    except Exception as e:
        logger.error(f"Error saat mencari video di YouTube API: {e}")
        return []

def fetch_video_comments(video_id: str, video_title: str = "", max_comments: int = MAX_COMMENTS_PER_VIDEO) -> List[Dict[str, Any]]:
    """Mengambil komentar dan balasan dari suatu video YouTube."""
    service = get_youtube_service()
    if not service:
        return []

    comments_data = []
    try:
        logger.info(f"Mengambil komentar untuk video: {video_id} ('{video_title[:40]}...')...")
        next_page_token = None

        while len(comments_data) < max_comments:
            request = service.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                maxResults=min(100, max_comments - len(comments_data)),
                pageToken=next_page_token,
                textFormat="plainText"
            )
            response = request.execute()

            for item in response.get("items", []):
                top_comment = item["snippet"]["topLevelComment"]["snippet"]
                comment_id = item["snippet"]["topLevelComment"]["id"]
                
                comments_data.append({
                    "source": "youtube",
                    "video_id": video_id,
                    "video_title": video_title,
                    "comment_id": comment_id,
                    "raw": {
                        "text": top_comment.get("textDisplay", ""),
                        "author": top_comment.get("authorDisplayName", "Anonim"),
                        "published_at": top_comment.get("publishedAt", ""),
                        "like_count": top_comment.get("likeCount", 0)
                    },
                    "scraped_at": datetime.now(timezone.utc).isoformat()
                })

                # Ambil replies jika ada
                if "replies" in item and "comments" in item["replies"]:
                    for reply_item in item["replies"]["comments"]:
                        reply_snippet = reply_item["snippet"]
                        comments_data.append({
                            "source": "youtube",
                            "video_id": video_id,
                            "video_title": video_title,
                            "comment_id": reply_item["id"],
                            "raw": {
                                "text": reply_snippet.get("textDisplay", ""),
                                "author": reply_snippet.get("authorDisplayName", "Anonim"),
                                "published_at": reply_snippet.get("publishedAt", ""),
                                "like_count": reply_snippet.get("likeCount", 0)
                            },
                            "scraped_at": datetime.now(timezone.utc).isoformat()
                        })

            next_page_token = response.get("nextPageToken")
            if not next_page_token or len(comments_data) >= max_comments:
                break

        logger.info(f"Berhasil mengambil {len(comments_data)} komentar dari video {video_id}.")
        return comments_data
    except Exception as e:
        logger.error(f"Error saat mengambil komentar video {video_id}: {e}")
        return []

def extract_video_id(url_or_id: str) -> str:
    """Mengekstrak YouTube video ID dari berbagai format URL atau ID mentah."""
    import re
    if not url_or_id:
        return ""
    url_or_id = url_or_id.strip()
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})(?:[?&/]|$)", url_or_id)
    if match:
        return match.group(1)
    if len(url_or_id) == 11 and re.match(r"^[0-9A-Za-z_-]{11}$", url_or_id):
        return url_or_id
    return url_or_id

def collect_from_video_ids(video_targets: List[str], max_comments_per_video: int = 100) -> List[Dict[str, Any]]:
    """
    Mengambil metadata video dan komentar dari daftar spesifik YouTube video ID atau URL.
    """
    service = get_youtube_service()
    all_comments = []

    # Dedup video IDs
    v_ids = []
    for item in video_targets:
        vid = extract_video_id(item)
        if vid and vid not in v_ids:
            v_ids.append(vid)

    logger.info(f"Mengambil komentar dari {len(v_ids)} video spesifik: {v_ids}")

    if service:
        for vid in v_ids:
            # Ambil judul video terlebih dahulu
            video_title = f"Video {vid}"
            try:
                v_req = service.videos().list(part="snippet", id=vid)
                v_res = v_req.execute()
                if v_res.get("items"):
                    video_title = v_res["items"][0]["snippet"]["title"]
            except Exception as e:
                logger.warning(f"Tidak dapat mengambil judul untuk video {vid}: {e}")

            comms = fetch_video_comments(
                video_id=vid,
                video_title=video_title,
                max_comments=max_comments_per_video
            )
            all_comments.extend(comms)
    else:
        logger.warning("YouTube API service tidak tersedia, beralih ke fallback sample mode.")
        all_comments = generate_mock_youtube_data(count=len(v_ids) * 30)

    return all_comments

def collect_youtube_data(query: str = None, video_ids: List[str] = None, count: int = 50) -> List[Dict[str, Any]]:
    """
    Fungsi utama collector YouTube.
    Bisa menerima daftar video_ids tertentu atau mencari via query.
    """
    if video_ids:
        return collect_from_video_ids(video_ids, max_comments_per_video=MAX_COMMENTS_PER_VIDEO)

    if query is None:
        query = DEFAULT_SEARCH_QUERIES[0]

    all_comments = []
    videos = search_youtube_videos(query=query)

    if videos:
        for vid in videos:
            comms = fetch_video_comments(
                video_id=vid["video_id"],
                video_title=vid["title"],
                max_comments=MAX_COMMENTS_PER_VIDEO
            )
            all_comments.extend(comms)
            if len(all_comments) >= count:
                break

    if not all_comments:
        logger.info("Menggunakan realistic mock YouTube comments data untuk pengujian/demo pipeline.")
        all_comments = generate_mock_youtube_data(count=count)

    return all_comments
