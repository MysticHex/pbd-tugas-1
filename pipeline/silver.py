"""
Silver Layer Handler
Membaca data mentah dari Bronze Layer, melakukan pembersihan teks melalui
NLP Preprocessing, dan menyimpan data terstruktur ke Silver Layer.
"""
from datetime import datetime, timezone
import logging
from typing import Dict, Any, Tuple

from config.settings import (
    get_mongo_db,
    COLLECTION_BRONZE_YOUTUBE,
    COLLECTION_BRONZE_NEWS,
    COLLECTION_SILVER_COMMENTS,
    COLLECTION_SILVER_NEWS
)
from pipeline.preprocessing import preprocess_text

logger = logging.getLogger(__name__)

def init_silver_indexes():
    """Membuat indeks pada Silver Layer untuk pencarian cepat dan pencegahan duplikasi."""
    db = get_mongo_db()
    try:
        db[COLLECTION_SILVER_COMMENTS].create_index("comment_id", unique=True)
        db[COLLECTION_SILVER_COMMENTS].create_index("published_at")
        db[COLLECTION_SILVER_NEWS].create_index("url", unique=True)
        logger.info("Indeks Silver Layer berhasil diinisialisasi.")
    except Exception as e:
        logger.warning(f"Catatan inisialisasi indeks Silver: {e}")

def process_bronze_to_silver_comments(batch_size: int = 500) -> Tuple[int, int]:
    """
    Mengambil data mentah dari bronze_youtube, membersihkan teks,
    dan menyimpan ke silver_comments.
    Mengembalikan (jumlah_diproses, jumlah_dilewati).
    """
    init_silver_indexes()
    db = get_mongo_db()
    bronze_col = db[COLLECTION_BRONZE_YOUTUBE]
    silver_col = db[COLLECTION_SILVER_COMMENTS]

    cursor = bronze_col.find({})
    processed_count = 0
    skipped_count = 0

    for doc in cursor:
        comment_id = doc.get("comment_id")
        raw_data = doc.get("raw", {})
        original_text = raw_data.get("text", "")

        # Preprocessing teks
        clean_text = preprocess_text(original_text)

        # Lewati komentar yang kosong atau terlalu pendek setelah cleaning
        if not clean_text or len(clean_text.split()) < 2:
            skipped_count += 1
            continue

        silver_doc = {
            "source": "youtube",
            "video_id": doc.get("video_id", ""),
            "video_title": doc.get("video_title", ""),
            "comment_id": comment_id,
            "text_original": original_text,
            "text_clean": clean_text,
            "author": raw_data.get("author", "Anonim"),
            "published_at": raw_data.get("published_at", ""),
            "like_count": int(raw_data.get("like_count", 0)),
            "language": "id",
            "processed_at": datetime.now(timezone.utc).isoformat()
        }

        try:
            silver_col.update_one(
                {"comment_id": comment_id},
                {"$set": silver_doc},
                upsert=True
            )
            processed_count += 1
        except Exception as e:
            logger.error(f"Gagal memproses silver comment {comment_id}: {e}")
            skipped_count += 1

    logger.info(f"Silver Comments: {processed_count} berhasil diproses, {skipped_count} dilewati.")
    return processed_count, skipped_count

def process_bronze_to_silver_news() -> Tuple[int, int]:
    """
    Mengambil data mentah dari bronze_news, merapikan data,
    dan menyimpan ke silver_news.
    Mengembalikan (jumlah_diproses, jumlah_dilewati).
    """
    init_silver_indexes()
    db = get_mongo_db()
    bronze_col = db[COLLECTION_BRONZE_NEWS]
    silver_col = db[COLLECTION_SILVER_NEWS]

    cursor = bronze_col.find({})
    processed_count = 0
    skipped_count = 0

    for doc in cursor:
        url = doc.get("url")
        raw_data = doc.get("raw", {})
        title = raw_data.get("title", "")
        content = raw_data.get("content", "")

        clean_title = preprocess_text(title)
        clean_content = preprocess_text(content)

        if not url or not content:
            skipped_count += 1
            continue

        silver_doc = {
            "source": "news",
            "url": url,
            "title": title,
            "title_clean": clean_title,
            "content": content,
            "content_clean": clean_content,
            "author": raw_data.get("author", "Redaksi"),
            "published_at": raw_data.get("published_at", ""),
            "language": "id",
            "processed_at": datetime.now(timezone.utc).isoformat()
        }

        try:
            silver_col.update_one(
                {"url": url},
                {"$set": silver_doc},
                upsert=True
            )
            processed_count += 1
        except Exception as e:
            logger.error(f"Gagal memproses silver news {url}: {e}")
            skipped_count += 1

    logger.info(f"Silver News: {processed_count} berhasil diproses, {skipped_count} dilewati.")
    return processed_count, skipped_count

def get_silver_stats() -> Dict[str, int]:
    """Mengambil jumlah data terkini pada Silver Layer."""
    db = get_mongo_db()
    comm_count = db[COLLECTION_SILVER_COMMENTS].count_documents({})
    news_count = db[COLLECTION_SILVER_NEWS].count_documents({})
    return {
        "silver_comments": comm_count,
        "silver_news": news_count,
        "total_silver": comm_count + news_count
    }
